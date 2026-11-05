"""Unit conversion. Canonical internal unit: millimetres.

Conversions use Decimal so explicit user dimensions are preserved exactly
(1 in = 25.4 mm and 1 ft = 304.8 mm are exact by definition).
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from enum import Enum


class Unit(str, Enum):
    MM = "mm"
    CM = "cm"
    M = "m"
    IN = "in"
    FT = "ft"


MM_PER_UNIT: dict[Unit, Decimal] = {
    Unit.MM: Decimal("1"),
    Unit.CM: Decimal("10"),
    Unit.M: Decimal("1000"),
    Unit.IN: Decimal("25.4"),
    Unit.FT: Decimal("304.8"),
}

_UNIT_ALIASES = {
    "mm": Unit.MM, "cm": Unit.CM, "m": Unit.M, "in": Unit.IN, "inch": Unit.IN,
    "inches": Unit.IN, '"': Unit.IN, "ft": Unit.FT, "foot": Unit.FT,
    "feet": Unit.FT, "'": Unit.FT,
}


def _to_decimal(value: object) -> Decimal:
    if isinstance(value, float):
        value = repr(value)  # avoid binary-float artefacts
    try:
        d = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"not a number: {value!r}") from exc
    if not d.is_finite():
        raise ValueError(f"value must be finite: {value!r}")
    return d


def to_mm(value: object, unit: Unit) -> Decimal:
    return _to_decimal(value) * MM_PER_UNIT[unit]


def from_mm(value_mm: object, unit: Unit) -> Decimal:
    return _to_decimal(value_mm) / MM_PER_UNIT[unit]


_FT_IN = re.compile(
    r"""^\s*(?P<ft>-?\d+(?:\.\d+)?)\s*(?:'|ft|feet)\s*(?:(?P<in>\d+(?:\.\d+)?)\s*(?:"|in|inch|inches)?)?\s*$""",
    re.IGNORECASE,
)
_SIMPLE = re.compile(
    r"""^\s*(?P<num>-?\d+(?:\.\d+)?)\s*(?P<unit>mm|cm|m|in|inch|inches|ft|feet|"|')\s*$""",
    re.IGNORECASE,
)


def parse_length_mm(text: str) -> Decimal:
    """Parse '4500 mm', '3.5 m', "12' 6\"" or '12ft 6in' into millimetres.

    Raises ValueError for anything ambiguous (for example a bare number with
    no unit): units are never guessed.
    """
    m = _FT_IN.match(text)
    if m:
        feet = Decimal(m.group("ft"))
        inches = Decimal(m.group("in") or "0")
        return to_mm(feet, Unit.FT) + to_mm(inches, Unit.IN)
    m = _SIMPLE.match(text)
    if m:
        return to_mm(m.group("num"), _UNIT_ALIASES[m.group("unit").lower()])
    raise ValueError(f"cannot parse length with explicit unit: {text!r}")
