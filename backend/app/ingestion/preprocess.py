"""Raster floor plan preprocessing: decode, skew estimation, deskew, denoise, threshold."""
from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class PreprocessResult:
    gray: np.ndarray        # deskewed, denoised grayscale
    ink: np.ndarray         # binary mask, 255 = drawing ink
    skew_deg: float         # correction angle applied (cv2 convention)
    transform: np.ndarray   # 2x3 affine matrix original -> output pixels


def decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("image could not be decoded")
    return img


def estimate_skew_deg(gray: np.ndarray, max_abs_deg: float = 15.0) -> float:
    """Dominant line orientation modulo 90 degrees, in image coordinates.

    Returns 0.0 when no reliable lines are found (never invents a skew).
    Passing the result to `rotate` straightens the drawing.
    """
    edges = cv2.Canny(gray, 50, 150)
    min_len = max(30, min(gray.shape) // 8)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 720, threshold=60,
                            minLineLength=min_len, maxLineGap=10)
    if lines is None:
        return 0.0
    angles, weights = [], []
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        ang = ((ang + 45.0) % 90.0) - 45.0
        angles.append(ang)
        weights.append(math.hypot(x2 - x1, y2 - y1))
    order = np.argsort(angles)
    a = np.array(angles)[order]
    w = np.array(weights)[order]
    cum = np.cumsum(w)
    median = float(a[np.searchsorted(cum, cum[-1] / 2.0)])
    return median if abs(median) <= max_abs_deg else 0.0


def rotate(img: np.ndarray, angle_deg: float, border: int = 255) -> tuple[np.ndarray, np.ndarray]:
    """Rotate with canvas expansion. Returns (image, 2x3 matrix original->output)."""
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle_deg, 1.0)
    cos, sin = abs(m[0, 0]), abs(m[0, 1])
    nw, nh = int(round(h * sin + w * cos)), int(round(h * cos + w * sin))
    m[0, 2] += nw / 2.0 - w / 2.0
    m[1, 2] += nh / 2.0 - h / 2.0
    out = cv2.warpAffine(img, m, (nw, nh), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=border)
    return out, m


def apply_transform(m: np.ndarray, pt: tuple[float, float]) -> tuple[float, float]:
    x, y = pt
    return (m[0, 0] * x + m[0, 1] * y + m[0, 2], m[1, 0] * x + m[1, 1] * y + m[1, 2])


def preprocess(gray: np.ndarray, deskew: bool = True) -> PreprocessResult:
    angle = estimate_skew_deg(gray) if deskew else 0.0
    if abs(angle) > 0.05:
        straightened, m = rotate(gray, angle)
    else:
        straightened, m = gray, np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float64)
        angle = 0.0
    den = cv2.medianBlur(straightened, 3)
    _, ink = cv2.threshold(den, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return PreprocessResult(den, ink, angle, m)


def ink_bounding_box(ink: np.ndarray) -> tuple[int, int, int, int]:
    """(x, y, w, h) of all ink pixels."""
    ys, xs = np.nonzero(ink)
    if xs.size == 0:
        raise ValueError("no drawing ink found")
    return int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
