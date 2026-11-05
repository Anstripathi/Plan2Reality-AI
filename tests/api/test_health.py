import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
try:
    from fastapi.testclient import TestClient
    from app.main import app
    HAVE_API = True
except ImportError:
    HAVE_API = False

from app.api.health import detect_environment
from app.core.config import load_settings


class EnvironmentTests(unittest.TestCase):
    def test_detect_environment_reports_each_tool_explicitly(self):
        env = detect_environment()
        for tool in ("blender", "ffmpeg", "tesseract", "git"):
            self.assertIn("available", env["optional_tools"][tool])

    def test_settings_validation(self):
        import os
        old = os.environ.get("P2R_MAX_UPLOAD_MB")
        try:
            os.environ["P2R_MAX_UPLOAD_MB"] = "0"
            with self.assertRaises(ValueError):
                load_settings()
            os.environ["P2R_MAX_UPLOAD_MB"] = "abc"
            with self.assertRaises(ValueError):
                load_settings()
        finally:
            if old is None:
                os.environ.pop("P2R_MAX_UPLOAD_MB", None)
            else:
                os.environ["P2R_MAX_UPLOAD_MB"] = old


@unittest.skipUnless(HAVE_API, "fastapi/httpx not installed")
class ApiTests(unittest.TestCase):
    def test_health_and_environment_endpoints(self):
        client = TestClient(app)
        self.assertEqual(client.get("/health").json()["status"], "ok")
        self.assertIn("optional_tools", client.get("/api/environment").json())


if __name__ == "__main__":
    unittest.main()
