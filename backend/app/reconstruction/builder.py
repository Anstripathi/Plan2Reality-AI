"""Plan -> meshes. Walls are assembled from exact boxes around real openings (no boolean ops),
so every dimension comes straight from the plan."""
from __future__ import annotations

from app.geometry.model import Floor, Opening, Plan, Wall
from app.reconstruction.mesh import Mesh


def _box(mesh: Mesh, wall: Wall, a: float, b: float, z0: float, z1: float) -> None:
    if b - a <= 1e-6 or z1 - z0 <= 1e-6:
        return
    h = wall.thickness_mm / 2.0
    quad = [wall.local_to_world(a, -h), wall.local_to_world(b, -h),
            wall.local_to_world(b, h), wall.local_to_world(a, h)]
    mesh.add_prism(quad, z0, z1)


def build_wall(wall: Wall, openings: list[Opening], elevation: float, height: float) -> Mesh:
    mesh = Mesh(f"wall_{wall.id}")
    z0, z1 = elevation, elevation + height
    cursor = -wall.start_extension_mm
    for o in sorted(openings, key=lambda o: o.offset_mm):
        a, b = o.offset_mm, o.offset_mm + o.width_mm
        _box(mesh, wall, cursor, a, z0, z1)
        _box(mesh, wall, a, b, z0, z0 + o.sill_mm)                        # below (windows)
        _box(mesh, wall, a, b, z0 + min(o.sill_mm + o.height_mm, height), z1)  # lintel
        cursor = b
    _box(mesh, wall, cursor, wall.length_mm + wall.end_extension_mm, z0, z1)
    return mesh


def build_floor(f: Floor) -> list[Mesh]:
    meshes: list[Mesh] = []
    if f.footprint:
        slab = Mesh(f"slab_L{f.level}")
        slab.add_prism(f.footprint, f.elevation_mm - f.slab_thickness_mm, f.elevation_mm)
        meshes.append(slab)
    for w in f.walls:
        ops = [o for o in f.openings if o.wall_id == w.id]
        meshes.append(build_wall(w, ops, f.elevation_mm, f.height_mm))
    for m in meshes:
        if m.name.startswith("wall_"):
            m.name = f"L{f.level}_{m.name}"
    return meshes


def build_plan(plan: Plan) -> list[Mesh]:
    out: list[Mesh] = []
    for f in plan.floors:
        out += build_floor(f)
    return out


def expected_wall_volume_mm3(wall: Wall, openings: list[Opening], height: float) -> float:
    total_len = wall.length_mm + wall.start_extension_mm + wall.end_extension_mm
    v = total_len * wall.thickness_mm * height
    for o in openings:
        v -= o.width_mm * (min(o.sill_mm + o.height_mm, height) - o.sill_mm) * wall.thickness_mm
    return v
