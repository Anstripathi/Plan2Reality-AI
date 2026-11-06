"""PDF and DXF readers. UNTESTED in the authoring sandbox (PyMuPDF/ezdxf not installed there).

Run `pytest tests/ingestion` locally after `pip install pymupdf ezdxf`; the
matching tests skip themselves when the libraries are absent.
"""
from __future__ import annotations

import io


class MissingDependencyError(RuntimeError):
    pass


def pdf_page_count(data: bytes) -> int:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise MissingDependencyError("PyMuPDF is required: pip install pymupdf") from exc
    with fitz.open(stream=data, filetype="pdf") as doc:
        return doc.page_count


def render_pdf_page_png(data: bytes, page: int = 0, dpi: int = 200) -> bytes:
    try:
        import fitz
    except ImportError as exc:
        raise MissingDependencyError("PyMuPDF is required: pip install pymupdf") from exc
    if not 36 <= dpi <= 600:
        raise ValueError("dpi must be within 36..600")
    with fitz.open(stream=data, filetype="pdf") as doc:
        if not 0 <= page < doc.page_count:
            raise ValueError("page out of range")
        return doc[page].get_pixmap(dpi=dpi).tobytes("png")


def dxf_line_segments(data: bytes) -> dict:
    """LINE and LWPOLYLINE segments in drawing units, plus the declared unit code ($INSUNITS)."""
    try:
        import ezdxf
    except ImportError as exc:
        raise MissingDependencyError("ezdxf is required: pip install ezdxf") from exc
    doc = ezdxf.read(io.StringIO(data.decode("utf-8", errors="replace")))
    segs = []
    for e in doc.modelspace().query("LINE"):
        segs.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
    for e in doc.modelspace().query("LWPOLYLINE"):
        pts = [(p[0], p[1]) for p in e.get_points("xy")]
        segs += list(zip(pts, pts[1:]))
        if e.closed and len(pts) > 2:
            segs.append((pts[-1], pts[0]))
    return {"insunits": doc.header.get("$INSUNITS", 0), "segments": segs}
