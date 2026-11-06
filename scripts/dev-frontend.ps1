# Run from repo root:  .\scripts\dev-frontend.ps1
$ErrorActionPreference = "Stop"
Push-Location frontend
npm run dev
Pop-Location
