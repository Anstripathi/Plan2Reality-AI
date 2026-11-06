# Roadmap
Phases follow the master prompt. Directories from the target layout (models, schemas, services, rendering, video, frontend editor/viewer/materials/timeline/hooks) are created in the phase that first needs them, not before.

| Phase | Status |
|---|---|
| 0 Repo and architecture | Done (frontend/backend not yet run through CI) |
| 1 Document ingestion | Partly done: validation, preprocess, calibration tested; PDF/DXF untested; no upload API/UI |
| 2 Recognition | Not started (needs real plans with known dimensions) |
| 3 Precision geometry | Partly done: IR, validation, comparison; no OCR, extraction, constraint solver, inspector UI |
| 4 First 3D | Partly done: walls, openings, slabs, GLB; no ceilings/frames; not opened in external viewer |
| 5 Editor | Not started |
| 6 Styling | Not started |
| 7 Complete building | Multi-floor stacking only; no stairs/roofs/terraces |
| 8 Rendering | Not started (needs Blender) |
| 9 Video | Not started (needs Blender + FFmpeg) |
| 10 Exports | GLB only; OBJ/STL/GLTF/DXF/IFC/images/video planned |
| 11 Hardening | Not started |

Next: Phase 2 on real sample plans; project/upload API (SQLAlchemy); then OBJ/STL/GLTF exporters.
