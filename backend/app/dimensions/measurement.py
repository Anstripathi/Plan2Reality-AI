"""Measurement with provenance, confidence and verification rules.

Only user-provided or CAD-derived values count as verified. OCR-, scale- and
AI-derived values stay unverified until a person explicitly confirms them.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum

from app.core.units import Unit, from_mm, to_mm


class Provenance(str, Enum):
    USER = "user"
    CAD = "cad"
    OCR = "ocr"
    SCALE = "scale"
    AI_ESTIMATED = "ai_estimated"


_AUTHORITATIVE = {Provenance.USER, Provenance.CAD}


@dataclass(frozen=True)
class Measurement:
    label: str
    value_mm: Decimal
    provenance: Provenance
    confidence: float
    original_value: Decimal
    original_unit: Unit
    user_confirmed: bool = False

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("label required")
        if self.value_mm <= 0:
            raise ValueError("length must be positive")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within 0..1")
        if self.provenance in _AUTHORITATIVE and self.confidence != 1.0:
            raise ValueError("user/CAD measurements carry confidence 1.0")

    @classmethod
    def create(cls, label: str, value: object, unit: Unit, provenance: Provenance,
               confidence: float | None = None) -> "Measurement":
        if confidence is None:
            if provenance not in _AUTHORITATIVE:
                raise ValueError(
                    "confidence must be stated for inferred measurements"
                )
            confidence = 1.0
        mm = to_mm(value, unit)
        return cls(label, mm, provenance, confidence, Decimal(str(value)), unit)

    @property
    def is_verified(self) -> bool:
        return self.provenance in _AUTHORITATIVE or self.user_confirmed

    def confirm_by_user(self) -> "Measurement":
        """Explicit human confirmation; the provenance is left unchanged."""
        return replace(self, user_confirmed=True)

    def in_unit(self, unit: Unit) -> Decimal:
        return from_mm(self.value_mm, unit)


def find_conflicts(measurements: list[Measurement],
                   tolerance_mm: Decimal = Decimal("1")) -> list[tuple[Measurement, Measurement]]:
    """Pairs sharing a label whose lengths differ by more than the tolerance."""
    out: list[tuple[Measurement, Measurement]] = []
    for i, a in enumerate(measurements):
        for b in measurements[i + 1:]:
            if a.label == b.label and abs(a.value_mm - b.value_mm) > tolerance_mm:
                out.append((a, b))
    return out
