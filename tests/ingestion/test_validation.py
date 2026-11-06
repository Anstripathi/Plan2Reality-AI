import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

import struct, tempfile
from app.ingestion.validation import UploadError, safe_filename, safe_join, validate_upload

PNG = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 800, 600) + b"\x08\x00\x00\x00\x00" + b"\x00" * 8
DXF = b"0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF\n"


class UploadTests(unittest.TestCase):
    def test_valid_png_and_dxf_and_pdf(self):
        v = validate_upload("plan.png", PNG)
        self.assertEqual((v.kind, v.width_px, v.height_px), ("png", 800, 600))
        self.assertEqual(validate_upload("a.dxf", DXF).kind, "dxf")
        self.assertEqual(validate_upload("a.pdf", b"%PDF-1.7\n...").kind, "pdf")

    def test_rejections(self):
        cases = [("a.png", b""), ("a.exe", PNG), ("a.pdf", PNG), ("a.png", b"MZ\x90\x00 not an image"),
                 ("a.png", b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 20000, 20000) + b"\x00" * 20)]
        for name, data in cases:
            with self.assertRaises(UploadError, msg=name):
                validate_upload(name, data)

    def test_size_limit(self):
        with self.assertRaises(UploadError):
            validate_upload("a.pdf", b"%PDF-" + b"0" * (2 * 1024 * 1024), max_mb=1)

    def test_path_traversal(self):
        self.assertEqual(safe_filename("../../etc/passwd"), "passwd")
        self.assertEqual(safe_filename("..\\..\\win.ini"), "win.ini")
        with tempfile.TemporaryDirectory() as d:
            p = safe_join(d, "../../x.png")
            self.assertEqual(p.parent, Path(d).resolve())
        with self.assertRaises(UploadError):
            safe_filename("../")


if __name__ == "__main__":
    unittest.main()
