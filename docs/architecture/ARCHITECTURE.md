# Architecture (Phase 0)
Pipeline: ingestion -> recognition -> dimension engine -> 2D geometry IR -> 3D generation -> editor/render/video/export.
- The 2D intermediate representation (IR) is engine-independent and editable; rendering engines consume it, never define it.
- Canonical unit is millimetres (`app/core/units.py`, Decimal arithmetic).
- Every dimension is a `Measurement` with provenance (user, cad, ocr, scale, ai_estimated), confidence and a verified flag. Only user/CAD values are verified unless a person confirms.
- Blender, FFmpeg and Tesseract are optional and detected at runtime (`/api/environment`).
- Backend: FastAPI + Pydantic. Frontend: React + TypeScript + Vite. SQLite via SQLAlchemy arrives with Phase 1.
