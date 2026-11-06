"""Scale calibration from a user-supplied reference length.

A raster drawing has no absolute scale by itself. Without a calibration the
caller gets an error, never a guessed value.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal

from app.core.units import Unit, to_mm
from app.dimensions.measurement import Measurement, Provenance

Point = tuple[float, float]


class CalibrationError(ValueError):
    pass


@dataclass(frozen=True)
class Calibration:
    mm_per_px: float
    reference_px: float
    reference_mm: Decimal
    endpoint_error_px: float

    @property
    def relative_uncertainty(self) -> float:
        """Worst-case relative scale error from +/- endpoint_error_px at both ends."""
        return (2.0 * self.endpoint_error_px) / self.reference_px

    def pixel_distance_to_mm(self, a: Point, b: Point) -> float:
        return math.dist(a, b) * self.mm_per_px

    def measure(self, label: str, a: Point, b: Point) -> Measurement:
        """Scale-derived measurement. Confidence is a heuristic (1 - relative
        uncertainty incl. the measured segment's own endpoint error), not a
        calibrated probability. Never verified automatically."""
        px = math.dist(a, b)
        if px <= 0:
            raise CalibrationError("zero-length segment")
        rel = self.relative_uncertainty + (2.0 * self.endpoint_error_px) / px
        conf = max(0.0, min(1.0, 1.0 - rel))
        mm = Decimal(repr(px * self.mm_per_px))
        return Measurement.create(label, mm, Unit.MM, Provenance.SCALE, confidence=conf)


def calibrate(p1: Point, p2: Point, real_length: object, unit: Unit,
              endpoint_error_px: float = 1.0) -> Calibration:
    px = math.dist(p1, p2)
    if px < 10:
        raise CalibrationError("reference segment too short (< 10 px) for a usable scale")
    mm = to_mm(real_length, unit)
    if mm <= 0:
        raise CalibrationError("reference length must be positive")
    return Calibration(float(mm) / px, px, mm, endpoint_error_px)
