# Development log
## Phase 0
Scaffold, units, measurement model, config, health endpoints, frontend shell, docs. Verified: stdlib unit tests only.

## Batch: Phase 1 ingestion + Phase 3 geometry core + Phase 4 mesh/GLB
Added upload validation, raster preprocessing, calibration, PDF/DXF readers (untested), geometry IR + validation, comparison/QA logic, mesh builder, GLB writer, independent GLB inspector.
Bugs found by tests: OpenCV 5 Hough output shape; `triangulate` accepted self-intersecting polygons (now rejected).
Result: 39 tests, 37 run and passed, 2 skipped (FastAPI, PyMuPDF/ezdxf not installed in sandbox).
