"""Health and environment reporting. Optional tools are detected, never assumed."""
from __future__ import annotations

import platform
import shutil


def detect_environment() -> dict:
    tools = {name: shutil.which(name) for name in ("blender", "ffmpeg", "tesseract", "git")}
    return {
        "python": platform.python_version(),
        "platform": platform.system(),
        "optional_tools": {k: {"available": v is not None, "path": v} for k, v in tools.items()},
    }
