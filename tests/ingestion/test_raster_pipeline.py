import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

import cv2, numpy as np
from decimal import Decimal
from app.core.units import Unit
from app.ingestion.calibration import CalibrationError, calibrate
from app.ingestion.preprocess import apply_transform, ink_bounding_box, preprocess, rotate

MM_PER_PX = 10.0   # ground truth: 100 px scale bar = 1000 mm


def make_plan():
    img = np.full((1000, 1400), 255, np.uint8)
    cv2.rectangle(img, (200, 200), (1200, 800), 0, 12)            # building, 1000x600 px centreline
    cv2.rectangle(img, (600, 200), (606, 800), 0, -1)             # partition
    cv2.line(img, (200, 900), (300, 900), 0, 4)                   # scale bar: 100 px
    cv2.line(img, (200, 890), (200, 910), 0, 4)
    cv2.line(img, (300, 890), (300, 910), 0, 4)
    return img


class RasterTests(unittest.TestCase):
    def run_case(self, theta, scale=1.0):
        base = make_plan()
        if scale != 1.0:
            base = cv2.resize(base, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        rot, m0 = rotate(base, theta) if theta else (base, np.array([[1, 0, 0], [0, 1, 0]], float))
        res = preprocess(rot)
        # map known scale-bar ends (original coords) through both transforms
        p1 = apply_transform(res.transform, apply_transform(m0, (200 * scale, 900 * scale)))
        p2 = apply_transform(res.transform, apply_transform(m0, (300 * scale, 900 * scale)))
        cal = calibrate(p1, p2, 1000, Unit.MM)
        x, y, w, h = ink_bounding_box(res.ink)
        # building outer box = 1012 x 612 px (line thickness 12) -> ground truth in mm
        return res, cal, w, h

    def test_skew_estimated_and_corrected(self):
        for theta in (3.2, -2.0, 0.0):
            res, cal, w, h = self.run_case(theta)
            self.assertAlmostEqual(res.skew_deg, -theta, delta=0.5, msg=f"theta={theta}")

    def test_measured_building_size_error_is_small_and_reported(self):
        truth_w, truth_h = 1012 * MM_PER_PX, 612 * MM_PER_PX
        for theta in (0.0, 3.2):
            res, cal, w, h = self.run_case(theta)
            # ink bbox includes the scale bar below the building (height) so use width only
            err_w = abs(w * cal.mm_per_px - truth_w) / truth_w * 100
            print(f"theta={theta}: measured width {w * cal.mm_per_px:.0f} mm vs {truth_w:.0f} mm, error {err_w:.2f}%")
            self.assertLess(err_w, 1.0)

    def test_low_resolution_has_lower_confidence(self):
        _, cal_hi, _, _ = self.run_case(0.0, 1.0)
        _, cal_lo, _, _ = self.run_case(0.0, 0.3)
        hi = cal_hi.measure("x", (0, 0), (500, 0)).confidence
        lo = cal_lo.measure("x", (0, 0), (150, 0)).confidence
        self.assertLess(lo, hi)

    def test_scale_measurements_are_never_verified(self):
        _, cal, _, _ = self.run_case(0.0)
        m = cal.measure("width", (0, 0), (1000, 0))
        self.assertFalse(m.is_verified)

    def test_bad_calibration_rejected(self):
        with self.assertRaises(CalibrationError):
            calibrate((0, 0), (3, 4), 1000, Unit.MM)
        with self.assertRaises(CalibrationError):
            calibrate((0, 0), (100, 0), 0, Unit.MM)

    def test_blank_image_gives_no_invented_skew(self):
        res = preprocess(np.full((400, 400), 255, np.uint8))
        self.assertEqual(res.skew_deg, 0.0)


if __name__ == "__main__":
    unittest.main()
