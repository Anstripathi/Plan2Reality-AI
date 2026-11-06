"""Upload validation: magic-byte type detection, safe names, size limits."""
from __future__ import annotations

import os
import re
import struct
from dataclasses import dataclass
from pathlib import Path

MAX_PIXELS = 100_000_000
_EXT_TO_KIND = {".pdf": "pdf", ".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".dxf": "dxf"}


class UploadError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedUpload:
    safe_name: str
    kind: str
    size_bytes: int
    width_px: int | None = None
    height_px: int | None = None


def safe_filename(name: str) -> str:
    base = re.split(r"[\\/]", name)[-1].strip().replace("\x00", "")
    base = re.sub(r"[^A-Za-z0-9._ -]", "_", base).lstrip(".")
    if not base or base in {".", ".."}:
        raise UploadError("invalid file name")
    return base[:120]


def safe_join(base_dir: str | os.PathLike, name: str) -> Path:
    """Join a (sanitised) name under base_dir; refuse anything that escapes it."""
    base = Path(base_dir).resolve()
    target = (base / safe_filename(name)).resolve()
    if base != target.parent:
        raise UploadError("path escapes storage directory")
    return target


def detect_kind(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    head = data[:4096].decode("ascii", errors="ignore")
    if re.search(r"^\s*0\s*\r?\n\s*SECTION\s*\r?\n", head, re.MULTILINE):
        return "dxf"
    return None


def image_dimensions(data: bytes, kind: str) -> tuple[int, int]:
    """Read pixel size from the header only (no full decode)."""
    if kind == "png":
        if len(data) < 24:
            raise UploadError("truncated PNG")
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    if kind == "jpeg":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + seg_len
        raise UploadError("JPEG size not found")
    raise UploadError("not a raster image")


def validate_upload(filename: str, data: bytes, max_mb: int = 50) -> ValidatedUpload:
    if not data:
        raise UploadError("empty file")
    if len(data) > max_mb * 1024 * 1024:
        raise UploadError(f"file exceeds {max_mb} MB limit")
    name = safe_filename(filename)
    ext_kind = _EXT_TO_KIND.get(Path(name).suffix.lower())
    if ext_kind is None:
        raise UploadError(f"unsupported file extension: {Path(name).suffix!r}")
    real = detect_kind(data)
    if real is None:
        raise UploadError("file content is not a recognised PDF, PNG, JPEG or DXF")
    if real != ext_kind:
        raise UploadError(f"extension says {ext_kind} but content is {real}")
    w = h = None
    if real in ("png", "jpeg"):
        w, h = image_dimensions(data, real)
        if w <= 0 or h <= 0 or w * h > MAX_PIXELS:
            raise UploadError(f"image dimensions not acceptable: {w}x{h}")
    return ValidatedUpload(name, real, len(data), w, h)
