# Testing
Run from the repository root:
```powershell
.\.venv\Scripts\python.exe -m pytest
# without pytest installed:
python -m unittest discover -s tests -p "test_*.py" -t .
```
| Folder | Covers |
|---|---|
| tests/unit | units, measurement provenance |
| tests/ingestion | upload validation, raster preprocessing + calibration (synthetic, rotated, low-res), PDF/DXF (skipped without pymupdf/ezdxf) |
| tests/geometry | polygons, plan validation, original-vs-reconstructed comparison |
| tests/integration | plan -> mesh -> GLB -> independent re-read; committed sample regression |
| tests/api | environment detection, settings; FastAPI endpoints (skipped without fastapi/httpx) |
| tests/fixtures | ground-truth data for the synthetic sample |

Ground truth comes from `app/geometry/samples.py` and `tests/fixtures/two_room_house_ground_truth.json`. Passing tests are necessary, not sufficient: inspect generated outputs (see `samples/`).
Not yet covered: frontend tests, video rendering, end-to-end, real scanned plans.
