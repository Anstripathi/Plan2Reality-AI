# Feature status ledger
| Item | Status | Notes |
|---|---|---|
| Unit conversion (mm/cm/m/in/ft) and length parsing | Tested | stdlib unit tests |
| Measurement provenance, confidence, conflicts | Tested | unit tests |
| Settings loader | Tested | validation tests |
| Environment detection | Tested | tools reported explicitly |
| FastAPI app (/health, /api/environment) | Implemented | not run in authoring sandbox (no network to install fastapi); run `pytest` locally |
| Frontend shell | Implemented | not built or type-checked yet; needs `npm install` |
| Everything in Modules A to N otherwise | Planned | |
