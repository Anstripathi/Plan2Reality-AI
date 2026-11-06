# API (current)
Interactive docs when the backend runs: http://127.0.0.1:8000/docs

| Method | Path | Purpose | Response |
|---|---|---|---|
| GET | /health | liveness | `{"status": "ok", "env": "development"}` |
| GET | /api/environment | Python version, OS, and which optional tools (blender, ffmpeg, tesseract, git) are found on PATH | `{"python": "...", "platform": "...", "optional_tools": {"ffmpeg": {"available": false, "path": null}, ...}}` |

No upload, project, geometry, render or export endpoints exist yet (see ROADMAP).
