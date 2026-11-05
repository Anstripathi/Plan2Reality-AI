# Plan2Reality AI
From 2D Blueprint to 3D Reality. A geometry-first architectural reconstruction platform (millimetres internally; user/CAD dimensions are the source of truth).

**Status: Phase 0 only.** See `docs/development/FEATURE_STATUS.md`. Nothing beyond the scaffold, unit conversion and measurement-provenance model exists yet.

## Setup (Windows, PowerShell)
```powershell
.\scripts\setup.ps1
```
## Run
```powershell
# terminal 1
cd backend; ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
# terminal 2
cd frontend; npm run dev
```
## Test
```powershell
.\.venv\Scripts\python.exe -m pytest
# or, without pytest:  python -m unittest discover -s tests -p "test_*.py" -t .
```
