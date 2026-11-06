# Feature status ledger
Levels: Planned / In progress / Implemented / Tested / Verified. "Tested" = automated tests pass; "Verified" = output independently inspected.

| Item | Status | Evidence / notes |
|---|---|---|
| Unit conversion, length parsing | Tested | exact Decimal arithmetic |
| Measurement provenance, confidence, conflicts | Tested | only user/CAD verified unless a person confirms |
| Upload validation (magic bytes, size, pixel limit, safe names, traversal) | Tested | no upload API endpoint wired yet |
| Raster preprocessing: skew estimate/deskew, denoise, Otsu threshold | Tested | synthetic plans only (clean, drawn lines); real scans untested |
| Scale calibration from a known reference length | Tested | synthetic: 0.10% width error (1 px); confidence is a heuristic |
| PDF page count/render, DXF line extraction | Implemented, UNTESTED here | needs `pip install pymupdf ezdxf`; tests auto-skip without them |
| 2D geometry IR (walls, openings, rooms, floors), JSON round-trip | Tested | |
| Geometry validation (openings, overlaps, closed exterior loop, floor alignment, polygons) | Tested | |
| Original-vs-reconstructed comparison, "fully verified" only if every required dimension passes | Tested | |
| Mesh generation: slabs, walls with real openings, multi-floor | Tested, Verified (south wall elevation inspected) | no ceilings, roofs, stairs, frames |
| GLB export + independent GLB inspector | Tested | size matches to 0.01 mm; wall volumes within 3e-6 relative; not yet opened in an external viewer |
| FastAPI app, frontend shell | Implemented | not run in authoring sandbox |
| Wall/room/door/window recognition from images, OCR dimensions, constraint solver | Planned | Phase 2/3 remainder |
| OBJ/STL/GLTF/DXF/IFC/PNG/JPG/MP4/WebM export, rendering, video, 3D editor, styling | Planned | |
