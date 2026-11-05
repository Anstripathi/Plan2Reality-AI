import sys, unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.core.units import Unit, from_mm, parse_length_mm, to_mm


class UnitTests(unittest.TestCase):
    def test_exact_conversions(self):
        self.assertEqual(to_mm("1", Unit.IN), Decimal("25.4"))
        self.assertEqual(to_mm("1", Unit.FT), Decimal("304.8"))
        self.assertEqual(to_mm("3.5", Unit.M), Decimal("3500.0"))
        self.assertEqual(to_mm("120", Unit.CM), Decimal("1200"))

    def test_float_input_has_no_binary_artifacts(self):
        self.assertEqual(to_mm(0.1, Unit.M), Decimal("100.0"))

    def test_round_trip(self):
        for unit in Unit:
            self.assertEqual(from_mm(to_mm("7.25", unit), unit), Decimal("7.25"))

    def test_parse(self):
        self.assertEqual(parse_length_mm("4500 mm"), Decimal("4500"))
        self.assertEqual(parse_length_mm("3.5 m"), Decimal("3500.0"))
        self.assertEqual(parse_length_mm("12' 6\""), Decimal("3810.0"))
        self.assertEqual(parse_length_mm("12ft 6in"), Decimal("3810.0"))
        self.assertEqual(parse_length_mm("10'"), Decimal("3048.0"))

    def test_unitless_or_garbage_rejected(self):
        for bad in ("4500", "abc", "", "5 parsecs", "nan m"):
            with self.assertRaises(ValueError):
                parse_length_mm(bad)

    def test_non_finite_rejected(self):
        with self.assertRaises(ValueError):
            to_mm(float("inf"), Unit.MM)


if __name__ == "__main__":
    unittest.main()
