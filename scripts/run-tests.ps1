# Run from repo root:  .\scripts\run-tests.ps1
$ErrorActionPreference = "Stop"
.\.venv\Scripts\python.exe -m pytest -v
