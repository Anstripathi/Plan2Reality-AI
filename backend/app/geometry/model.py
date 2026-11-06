"""Engine-independent, editable 2D architectural intermediate representation (millimetres)."""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum

Point = tuple[float, float]


class OpeningKind(str, Enum):
    DOOR = "door"
    WINDOW = "window"


@dataclass
class Wall:
    id: str
    start: Point
    end: Point
    thickness_mm: float
    exterior: bool = False
    start_extension_mm: float = 0.0
    end_extension_mm: float = 0.0

    @property
    def length_mm(self) -> float:
        return math.dist(self.start, self.end)

    @property
    def direction(self) -> Point:
        L = self.length_mm
        return ((self.end[0] - self.start[0]) / L, (self.end[1] - self.start[1]) / L)

    @property
    def normal(self) -> Point:
        ux, uy = self.direction
        return (-uy, ux)

    def local_to_world(self, u: float, s: float) -> Point:
        """u along the centerline from start, s across (positive = left)."""
        ux, uy = self.direction
        nx, ny = self.normal
        return (self.start[0] + ux * u + nx * s, self.start[1] + uy * u + ny * s)

    def polygon(self) -> list[Point]:
        h = self.thickness_mm / 2.0
        a, b = -self.start_extension_mm, self.length_mm + self.end_extension_mm
        return [self.local_to_world(a, -h), self.local_to_world(b, -h),
                self.local_to_world(b, h), self.local_to_world(a, h)]


@dataclass
class Opening:
    id: str
    wall_id: str
    offset_mm: float      # from wall start along the centerline
    width_mm: float
    height_mm: float
    sill_mm: float = 0.0
    kind: OpeningKind = OpeningKind.DOOR


@dataclass
class Room:
    id: str
    name: str
    polygon: list[Point]


@dataclass
class Floor:
    level: int
    elevation_mm: float
    height_mm: float
    slab_thickness_mm: float = 150.0
    walls: list[Wall] = field(default_factory=list)
    openings: list[Opening] = field(default_factory=list)
    rooms: list[Room] = field(default_factory=list)
    footprint: list[Point] = field(default_factory=list)

    def wall(self, wall_id: str) -> Wall:
        for w in self.walls:
            if w.id == wall_id:
                return w
        raise KeyError(wall_id)


@dataclass
class Plan:
    name: str
    floors: list[Floor] = field(default_factory=list)
    unit: str = "mm"

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Plan":
        d = json.loads(text)
        if d.get("unit") != "mm":
            raise ValueError("plan unit must be mm")
        pt = lambda p: (float(p[0]), float(p[1]))
        floors = []
        for f in d["floors"]:
            floors.append(Floor(
                level=f["level"], elevation_mm=f["elevation_mm"], height_mm=f["height_mm"],
                slab_thickness_mm=f["slab_thickness_mm"],
                walls=[Wall(w["id"], pt(w["start"]), pt(w["end"]), w["thickness_mm"], w["exterior"],
                            w["start_extension_mm"], w["end_extension_mm"]) for w in f["walls"]],
                openings=[Opening(o["id"], o["wall_id"], o["offset_mm"], o["width_mm"], o["height_mm"],
                                  o["sill_mm"], OpeningKind(o["kind"])) for o in f["openings"]],
                rooms=[Room(r["id"], r["name"], [pt(p) for p in r["polygon"]]) for r in f["rooms"]],
                footprint=[pt(p) for p in f["footprint"]]))
        return cls(d["name"], floors, "mm")
