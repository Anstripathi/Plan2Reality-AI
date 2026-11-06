import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.ingestion.pdf_dxf import MissingDependencyError, dxf_line_segments, pdf_page_count

try:
    import ezdxf, fitz
    HAVE = True
except ImportError:
    HAVE = False


class PdfDxfTests(unittest.TestCase):
    def test_missing_dependency_is_explicit(self):
        if HAVE:
            self.skipTest("libraries installed")
        with self.assertRaises(MissingDependencyError):
            pdf_page_count(b"%PDF-1.4")

    @unittest.skipUnless(HAVE, "pymupdf and ezdxf not installed")
    def test_dxf_roundtrip(self):
        import io
        doc = ezdxf.new(); doc.header["$INSUNITS"] = 4
        doc.modelspace().add_line((0, 0), (5000, 0))
        buf = io.StringIO(); doc.write(buf)
        out = dxf_line_segments(buf.getvalue().encode())
        self.assertEqual(out["insunits"], 4)
        self.assertEqual(out["segments"], [((0.0, 0.0), (5000.0, 0.0))])


if __name__ == "__main__":
    unittest.main()
