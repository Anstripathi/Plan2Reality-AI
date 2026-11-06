# Run from repo root:  .\scripts\dev-backend.ps1
$ErrorActionPreference = "Stop"
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw "Run .\scripts\setup.ps1 first" }
Push-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
Pop-Location
