# Development log
## Phase 0
Scaffold, units, measurement model, config, health endpoints, frontend shell, docs. Verified: stdlib unit tests only.

## Batch: Phase 1 ingestion + Phase 3 geometry core + Phase 4 mesh/GLB
Added upload validation, raster preprocessing, calibration, PDF/DXF readers (untested), geometry IR + validation, comparison/QA logic, mesh builder, GLB writer, independent GLB inspector.
Bugs found by tests: OpenCV 5 Hough output shape; `triangulate` accepted self-intersecting polygons (now rejected).
Result: 39 tests, 37 run and passed, 2 skipped (FastAPI, PyMuPDF/ezdxf not installed in sandbox).

## Restructure to the master prompt's layout
Moved raster preprocessing to `backend/app/vision/`; frontend split into components/pages/services/types; added API, TESTING and ROADMAP docs, root `pytest.ini`, run scripts (`scripts/*.ps1`), generated sample (`samples/two_room_house`, regenerate with `scripts/generate_samples.py`) and a committed-sample regression test. 42 tests: 40 passed, 2 skipped. Frontend refactor is not type-checked or built (no npm packages in the authoring sandbox).
