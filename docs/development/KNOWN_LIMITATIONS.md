# Known limitations
- Authored in a Linux sandbox (Python 3.12, no package network). Target is Windows + Python 3.11. FastAPI, frontend build, PowerShell setup, PyMuPDF and ezdxf code are unverified until run locally.
- Raster tests use clean synthetic drawings. Accuracy on real scans, photos or hand-drawn plans is unknown and must be measured against a ground-truth dataset.
- Calibration confidence is a heuristic, not a calibrated probability.
- Recognition (walls, rooms, doors, windows, OCR) is not implemented; plans enter the system as structured data.
- No constraint solver yet: contradictions are detected and reported, not solved.
- Meshes have no normals/materials, ceilings, roofs, stairs or window frames. Overlapping wall boxes at partition joints are not merged.
- GLB validated by an in-repo parser only; open it in an external viewer (e.g. Blender, gltf viewer) as a second check.
- Image size is checked from headers; full decode of a hostile image is not sandboxed.
