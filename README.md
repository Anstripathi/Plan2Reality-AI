# Plan2Reality AI
From 2D Blueprint to 3D Reality. A geometry-first architectural reconstruction platform: millimetres internally, user/CAD dimensions are the source of truth, nothing is called "verified" unless it is.

**Status: early development.** Built and tested: units, measurement provenance, upload validation, raster preprocessing and calibration, 2D geometry model and validation, mesh generation, GLB export with independent validation. Not built: recognition from images, OCR, constraint solver, editor, styling, rendering, video, most exports. Details: `docs/development/FEATURE_STATUS.md`, `docs/development/ROADMAP.md`, `docs/development/KNOWN_LIMITATIONS.md`.

## Setup (Windows, PowerShell, from the repo root)
```powershell
.\scripts\setup.ps1
```
## Run
```powershell
.\scripts\dev-backend.ps1     # terminal 1: http://127.0.0.1:8000  (API docs at /docs)
.\scripts\dev-frontend.ps1    # terminal 2: http://localhost:5173
```
## Test
```powershell
.\scripts\run-tests.ps1
```
Optional tools (Blender, FFmpeg, Tesseract) are detected on PATH and shown on the home page; none is needed yet.

## Layout
`backend/app` (api, core, dimensions, geometry, ingestion, vision, reconstruction, exporters, validators) · `frontend/src` (components, pages, services, types) · `tests` · `docs` (architecture, api, development, testing) · `samples` (synthetic plan with ground truth) · `scripts`.
Directories for later phases (rendering, video, editor, viewer, timeline, materials, models, schemas) are added when their phase starts.
