"""Environment-driven settings (stdlib only, no secrets stored in code)."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str
    storage_dir: str
    max_upload_mb: int
    database_url: str


def load_settings() -> Settings:
    try:
        max_mb = int(os.environ.get("P2R_MAX_UPLOAD_MB", "50"))
    except ValueError as exc:
        raise ValueError("P2R_MAX_UPLOAD_MB must be an integer") from exc
    if max_mb <= 0:
        raise ValueError("P2R_MAX_UPLOAD_MB must be positive")
    return Settings(
        env=os.environ.get("P2R_ENV", "development"),
        storage_dir=os.environ.get("P2R_STORAGE_DIR", "storage"),
        max_upload_mb=max_mb,
        database_url=os.environ.get(
            "P2R_DATABASE_URL", "sqlite:///./storage/plan2reality.sqlite3"
        ),
    )
