import sys, unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.core.units import Unit
from app.dimensions.measurement import Measurement, Provenance, find_conflicts


class MeasurementTests(unittest.TestCase):
    def test_user_value_preserved_exactly_and_verified(self):
        m = Measurement.create("living width", "4.2", Unit.M, Provenance.USER)
        self.assertEqual(m.value_mm, Decimal("4200.0"))
        self.assertEqual(m.original_unit, Unit.M)
        self.assertTrue(m.is_verified)

    def test_inferred_requires_confidence_and_is_unverified(self):
        with self.assertRaises(ValueError):
            Measurement.create("wall", 3000, Unit.MM, Provenance.AI_ESTIMATED)
        for prov in (Provenance.OCR, Provenance.SCALE, Provenance.AI_ESTIMATED):
            m = Measurement.create("wall", 3000, Unit.MM, prov, confidence=0.8)
            self.assertFalse(m.is_verified)

    def test_explicit_confirmation_verifies_without_changing_provenance(self):
        m = Measurement.create("wall", 3000, Unit.MM, Provenance.OCR, confidence=0.7)
        c = m.confirm_by_user()
        self.assertTrue(c.is_verified)
        self.assertEqual(c.provenance, Provenance.OCR)
        self.assertFalse(m.is_verified)

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError):
            Measurement.create("x", 0, Unit.MM, Provenance.USER)
        with self.assertRaises(ValueError):
            Measurement.create("x", 10, Unit.MM, Provenance.OCR, confidence=1.5)
        with self.assertRaises(ValueError):
            Measurement.create("x", 10, Unit.MM, Provenance.USER, confidence=0.5)

    def test_conflict_detection(self):
        a = Measurement.create("bed1 width", 3600, Unit.MM, Provenance.USER)
        b = Measurement.create("bed1 width", 3.65, Unit.M, Provenance.OCR, confidence=0.9)
        c = Measurement.create("bed1 width", 3600.5, Unit.MM, Provenance.CAD)
        self.assertEqual(find_conflicts([a, b]), [(a, b)])
        self.assertEqual(find_conflicts([a, c]), [])


if __name__ == "__main__":
    unittest.main()
