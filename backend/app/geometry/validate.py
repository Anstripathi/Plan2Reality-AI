"""Geometry validation. Reports problems; never silently repairs them."""
from __future__ import annotations

import math
from dataclasses import dataclass

from app.geometry.model import Floor, Plan
from app.geometry.polygon import is_simple, signed_area

TOL_MM = 1.0


@dataclass(frozen=True)
class Issue:
    severity: str   # "error" | "warning"
    code: str
    message: str
    object_id: str = ""


def validate_floor(f: Floor) -> list[Issue]:
    out: list[Issue] = []
    ids = [w.id for w in f.walls]
    for dup in {i for i in ids if ids.count(i) > 1}:
        out.append(Issue("error", "duplicate_wall_id", f"wall id used twice: {dup}", dup))
    for w in f.walls:
        if w.length_mm < TOL_MM:
            out.append(Issue("error", "zero_length_wall", "wall has no length", w.id))
        if w.thickness_mm <= 0:
            out.append(Issue("error", "bad_thickness", "wall thickness must be positive", w.id))
    by_wall: dict[str, list] = {}
    for o in f.openings:
        try:
            w = f.wall(o.wall_id)
        except KeyError:
            out.append(Issue("error", "opening_unknown_wall", f"wall {o.wall_id} not found", o.id))
            continue
        if o.width_mm <= 0 or o.height_mm <= 0 or o.sill_mm < 0 or o.offset_mm < 0:
            out.append(Issue("error", "bad_opening_size", "opening size/offset invalid", o.id))
        if o.offset_mm + o.width_mm > w.length_mm + TOL_MM:
            out.append(Issue("error", "opening_exceeds_wall", "opening runs past the wall end", o.id))
        if o.sill_mm + o.height_mm > f.height_mm + TOL_MM:
            out.append(Issue("error", "opening_exceeds_height", "opening taller than the floor height", o.id))
        by_wall.setdefault(o.wall_id, []).append(o)
    for wid, ops in by_wall.items():
        ops.sort(key=lambda o: o.offset_mm)
        for a, b in zip(ops, ops[1:]):
            if a.offset_mm + a.width_mm > b.offset_mm + 1e-6:
                out.append(Issue("error", "openings_overlap", f"{a.id} overlaps {b.id}", wid))
    for r in f.rooms:
        if not is_simple(r.polygon):
            out.append(Issue("error", "invalid_room_polygon", "room polygon self-intersects or is degenerate", r.id))
    if f.footprint and not is_simple(f.footprint):
        out.append(Issue("error", "invalid_footprint", "footprint polygon is invalid", ""))
    ext = [w for w in f.walls if w.exterior and w.length_mm >= TOL_MM]
    if ext:
        ends = [p for w in ext for p in (w.start, w.end)]
        for i, p in enumerate(ends):
            matches = sum(1 for j, q in enumerate(ends) if j != i and math.dist(p, q) <= TOL_MM)
            if matches != 1:
                out.append(Issue("error", "exterior_not_closed",
                                 f"exterior wall endpoint ({p[0]:.1f}, {p[1]:.1f}) does not meet exactly one other", ""))
    return out


def validate_plan(plan: Plan) -> list[Issue]:
    out: list[Issue] = []
    levels = [f.level for f in plan.floors]
    if len(set(levels)) != len(levels):
        out.append(Issue("error", "duplicate_level", "two floors share a level number"))
    ordered = sorted(plan.floors, key=lambda f: f.level)
    for a, b in zip(ordered, ordered[1:]):
        if abs(b.elevation_mm - (a.elevation_mm + a.height_mm)) > TOL_MM:
            out.append(Issue("error", "floor_misaligned",
                             f"level {b.level} elevation does not equal level {a.level} elevation + height"))
    for f in plan.floors:
        out += validate_floor(f)
    return out


def has_errors(issues: list[Issue]) -> bool:
    return any(i.severity == "error" for i in issues)
