import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

import tempfile, os
from app.dimensions.compare import compare
from app.dimensions.measurement import Measurement, Provenance
from app.core.units import Unit
from app.exporters.glb import write_glb
from app.geometry.samples import GROUND_TRUTH as GT, two_room_house
from app.reconstruction.builder import build_plan, expected_wall_volume_mm3
from app.validators.glb_check import inspect_glb


class PlanToGlbTests(unittest.TestCase):
    def export(self, plan):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "m.glb")
        write_glb(build_plan(plan), path)
        return inspect_glb(path)

    def test_single_floor_dimensions_and_openings_survive_export(self):
        plan = two_room_house()
        rep = self.export(plan)
        f = plan.floors[0]
        sx, sy, sz = rep["size_mm"]
        print(f"GLB size mm: {sx:.4f} x {sy:.4f} x {sz:.4f}")
        self.assertAlmostEqual(sx, GT["outer_width"], delta=0.01)
        self.assertAlmostEqual(sy, GT["outer_length"], delta=0.01)
        self.assertAlmostEqual(sz, GT["floor_height"] + f.slab_thickness_mm, delta=0.01)
        by_name = {n["name"]: n for n in rep["nodes"]}
        for w in f.walls:
            ops = [o for o in f.openings if o.wall_id == w.id]
            exp = expected_wall_volume_mm3(w, ops, f.height_mm)
            got = by_name[f"L0_wall_{w.id}"]["volume_mm3"]
            print(f"wall {w.id}: expected {exp:.1f} got {got:.1f} rel.err {abs(got - exp) / exp:.2e}")
            self.assertLess(abs(got - exp) / exp, 1e-4)
            self.assertEqual(by_name[f"L0_wall_{w.id}"]["degenerate_triangles"], 0)
        slab = by_name["slab_L0"]
        self.assertAlmostEqual(slab["volume_mm3"], 10000 * 8000 * 150, delta=1e4)

    def test_user_dimension_check_against_reopened_file(self):
        rep = self.export(two_room_house())
        user = Measurement.create("outer_width", 10, Unit.M, Provenance.USER)
        self.assertEqual(compare(user, rep["size_mm"][0]).status, "pass")

    def test_two_floor_building_height(self):
        rep = self.export(two_room_house(2))
        self.assertAlmostEqual(rep["size_mm"][2], 2 * 2800 + 150, delta=0.01)

    def test_unit_scale_is_metres_in_file(self):
        rep = self.export(two_room_house())
        self.assertAlmostEqual(rep["bbox_min_mm"][0], 0.0, delta=0.01)

    def test_empty_export_refused(self):
        with self.assertRaises(ValueError):
            write_glb([], "x.glb")


if __name__ == "__main__":
    unittest.main()
