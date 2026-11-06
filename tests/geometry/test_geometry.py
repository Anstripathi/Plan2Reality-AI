import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

import copy
from app.geometry.model import Opening, Plan
from app.geometry.polygon import is_simple, signed_area, triangulate
from app.geometry.samples import GROUND_TRUTH as GT, two_room_house
from app.geometry.validate import has_errors, validate_plan
from app.dimensions.compare import compare, outer_size_mm, room_size_mm, summarize
from app.dimensions.measurement import Measurement, Provenance
from app.core.units import Unit


def codes(plan):
    return {i.code for i in validate_plan(plan)}


class PolygonTests(unittest.TestCase):
    def test_l_shape_triangulation_area(self):
        L = [(0, 0), (6000, 0), (6000, 2000), (2000, 2000), (2000, 5000), (0, 5000)]
        pts, tris = triangulate(L)
        total = sum(abs(signed_area([pts[a], pts[b], pts[c]])) for a, b, c in tris)
        self.assertAlmostEqual(total, abs(signed_area(L)), places=6)
        self.assertEqual(len(tris), 4)

    def test_bowtie_not_simple(self):
        self.assertFalse(is_simple([(0, 0), (10, 10), (10, 0), (0, 10)]))
        with self.assertRaises(ValueError):
            triangulate([(0, 0), (10, 10), (10, 0), (0, 10)])


class PlanTests(unittest.TestCase):
    def test_sample_is_valid_and_dimensions_exact(self):
        p = two_room_house()
        self.assertFalse(has_errors(validate_plan(p)))
        f = p.floors[0]
        self.assertEqual(outer_size_mm(f), (GT["outer_width"], GT["outer_length"]))
        self.assertEqual(room_size_mm(f.rooms[0]), (GT["left_room_width"], GT["room_length"]))
        self.assertEqual(room_size_mm(f.rooms[1]), (GT["right_room_width"], GT["room_length"]))

    def test_json_roundtrip_preserves_everything(self):
        p = two_room_house(2)
        self.assertEqual(Plan.from_json(p.to_json()), p)

    def test_detects_invalid_geometry(self):
        p = two_room_house(); f = p.floors[0]
        f.openings.append(Opening("too_wide", "S", 9000, 1500, 2100))
        f.openings.append(Opening("overlap", "S", 7500, 1000, 2100))
        f.openings.append(Opening("tall", "P1", 100, 500, 3500))
        f.openings.append(Opening("ghost", "NOPE", 0, 100, 100))
        f.walls[2].end = (f.walls[2].end[0], f.walls[2].end[1] - 500)      # open the exterior loop
        c = codes(p)
        for expected in ("opening_exceeds_wall", "openings_overlap", "opening_exceeds_height",
                         "opening_unknown_wall", "exterior_not_closed"):
            self.assertIn(expected, c)

    def test_floor_misalignment_and_bad_room(self):
        p = two_room_house(2)
        p.floors[1].elevation_mm += 100
        p.floors[0].rooms[0].polygon = [(0, 0), (10, 10), (10, 0), (0, 10)]
        c = codes(p)
        self.assertIn("floor_misaligned", c)
        self.assertIn("invalid_room_polygon", c)


class CompareTests(unittest.TestCase):
    def test_verified_pass_fail_and_reported(self):
        user = Measurement.create("outer_width", 10, Unit.M, Provenance.USER)
        self.assertEqual(compare(user, 10000.0).status, "pass")
        self.assertEqual(compare(user, 10002.0).status, "fail")
        ocr = Measurement.create("outer_width", 9.9, Unit.M, Provenance.OCR, confidence=0.8)
        c = compare(ocr, 10000.0)
        self.assertEqual(c.status, "reported")
        self.assertAlmostEqual(float(c.percent_error), 1.0101, places=3)

    def test_partial_match_is_not_whole_building_verified(self):
        user = Measurement.create("outer_width", 10, Unit.M, Provenance.USER)
        s = summarize([compare(user, 10000.0)], ["outer_width", "outer_length"])
        self.assertFalse(s["fully_verified"])
        self.assertEqual(s["missing"], ["outer_length"])
        s2 = summarize([compare(user, 10000.0)], ["outer_width"])
        self.assertTrue(s2["fully_verified"])


if __name__ == "__main__":
    unittest.main()
