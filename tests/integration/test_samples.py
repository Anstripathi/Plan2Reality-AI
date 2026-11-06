import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.geometry.model import Plan
from app.geometry.samples import GROUND_TRUTH, two_room_house
from app.geometry.validate import has_errors, validate_plan
from app.validators.glb_check import inspect_glb

SAMPLE = ROOT / "samples" / "two_room_house"
FIXTURE = ROOT / "tests" / "fixtures" / "two_room_house_ground_truth.json"


class CommittedSampleTests(unittest.TestCase):
    def test_fixture_matches_code_ground_truth(self):
        fx = json.loads(FIXTURE.read_text())
        for k, v in GROUND_TRUTH.items():
            self.assertEqual(fx[k], v)

    def test_plan_json_is_valid_and_current(self):
        plan = Plan.from_json((SAMPLE / "plan.json").read_text())
        self.assertEqual(plan, two_room_house())
        self.assertFalse(has_errors(validate_plan(plan)))

    def test_committed_glb_preserves_dimensions(self):
        rep = inspect_glb(SAMPLE / "model.glb")
        self.assertAlmostEqual(rep["size_mm"][0], GROUND_TRUTH["outer_width"], delta=0.01)
        self.assertAlmostEqual(rep["size_mm"][1], GROUND_TRUTH["outer_length"], delta=0.01)


if __name__ == "__main__":
    unittest.main()
