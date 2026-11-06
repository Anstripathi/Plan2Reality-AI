from __future__ import annotations

from dataclasses import dataclass, field

from app.geometry.polygon import Point, triangulate

V3 = tuple[float, float, float]


@dataclass
class Mesh:
    name: str
    vertices: list[V3] = field(default_factory=list)
    triangles: list[tuple[int, int, int]] = field(default_factory=list)

    def add_prism(self, poly: list[Point], z0: float, z1: float) -> None:
        """Extrude a simple polygon between z0 and z1 (outward-facing triangles)."""
        pts, tris = triangulate(poly)
        n, base = len(pts), len(self.vertices)
        self.vertices += [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
        for a, b, c in tris:
            self.triangles.append((base + n + a, base + n + b, base + n + c))   # top
            self.triangles.append((base + a, base + c, base + b))               # bottom
        for i in range(n):
            j = (i + 1) % n
            self.triangles.append((base + i, base + j, base + n + j))
            self.triangles.append((base + i, base + n + j, base + n + i))

    def volume_mm3(self) -> float:
        v = 0.0
        for a, b, c in self.triangles:
            (ax, ay, az), (bx, by, bz), (cx, cy, cz) = self.vertices[a], self.vertices[b], self.vertices[c]
            v += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)
        return v / 6.0

    def bbox(self) -> tuple[V3, V3]:
        xs, ys, zs = zip(*self.vertices)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
