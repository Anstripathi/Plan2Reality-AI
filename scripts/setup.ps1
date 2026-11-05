# Run from the repository root in PowerShell:  .\scripts\setup.ps1
$ErrorActionPreference = "Stop"
foreach ($tool in "python", "node", "npm", "git") {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool not found on PATH" }
}
python --version; node --version; npm --version; git --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
Push-Location frontend; npm install; Pop-Location
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Setup complete."
foreach ($t in "blender", "ffmpeg", "tesseract") {
    $c = Get-Command $t -ErrorAction SilentlyContinue
    if ($c) { Write-Host "$t : $($c.Source)" } else { Write-Host "$t : not found (optional for now)" }
}
