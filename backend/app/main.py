from fastapi import FastAPI

from app.api.health import detect_environment
from app.core.config import load_settings

settings = load_settings()
app = FastAPI(title="Plan2Reality AI", version="0.0.1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.env}


@app.get("/api/environment")
def environment() -> dict:
    return detect_environment()
