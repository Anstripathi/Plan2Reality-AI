"""Original vs reconstructed dimension comparison (feeds the QA dashboard)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.dimensions.measurement import Measurement, Provenance
from app.geometry.model import Floor, Room, Wall
from app.geometry.polygon import Point

TOLERANCE_MM = Decimal("1")


@dataclass(frozen=True)
class DimensionCheck:
    label: str
    original_mm: Decimal
    reconstructed_mm: Decimal
    difference_mm: Decimal
    percent_error: Decimal
    provenance: Provenance
    reference_verified: bool
    status: str   # "pass" | "fail" | "reported" (reference not verified: error shown, no pass/fail)


def compare(m: Measurement, reconstructed_mm: float) -> DimensionCheck:
    rec = Decimal(repr(float(reconstructed_mm)))
    diff = rec - m.value_mm
    pct = abs(diff) / m.value_mm * 100
    if not m.is_verified:
        status = "reported"
    else:
        status = "pass" if abs(diff) <= TOLERANCE_MM else "fail"
    return DimensionCheck(m.label, m.value_mm, rec, diff, pct, m.provenance, m.is_verified, status)


def bbox(points: list[Point]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def outer_size_mm(floor: Floor) -> tuple[float, float]:
    pts = [p for w in floor.walls if w.exterior for p in w.polygon()]
    x0, y0, x1, y1 = bbox(pts)
    return x1 - x0, y1 - y0


def room_size_mm(room: Room) -> tuple[float, float]:
    """Bounding-box width/length (meaningful for rectangular rooms)."""
    x0, y0, x1, y1 = bbox(room.polygon)
    return x1 - x0, y1 - y0


def summarize(checks: list[DimensionCheck], required_labels: list[str]) -> dict:
    present = {c.label for c in checks}
    missing = [l for l in required_labels if l not in present]
    n_pass = sum(c.status == "pass" for c in checks)
    n_fail = sum(c.status == "fail" for c in checks)
    n_rep = sum(c.status == "reported" for c in checks)
    return {"checked": len(checks), "pass": n_pass, "fail": n_fail, "unverified_reference": n_rep,
            "missing": missing,
            "fully_verified": bool(checks) and not missing and n_fail == 0 and n_rep == 0}
