from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.model_service import ToxicityModelService


ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"


class AnalyzeRequest(BaseModel):
    comment: str = Field(..., min_length=1, max_length=5000)


class CategoryScore(BaseModel):
    label: str
    rawLabel: str
    score: int


class AnalyzeResponse(BaseModel):
    comment: str
    confidence: int
    isToxic: bool
    model: str
    primarySignal: str
    recommendation: str
    score: int
    signals: list[str]
    summary: str
    threshold: int
    verdict: str
    categories: list[CategoryScore]


class HealthResponse(BaseModel):
    status: str
    model: str
    modelLoaded: bool
    threshold: int
    lastError: Optional[str]


model_service = ToxicityModelService()


def env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if env_flag("PRELOAD_MODEL_ON_STARTUP"):
        model_service.ensure_loaded()

    yield


app = FastAPI(
    title="ToneCheck Local ML API",
    version="1.0.0",
    description="Local toxicity detection API backed by a Hugging Face model.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(**model_service.metadata())


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = model_service.analyze(payload.comment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AnalyzeResponse(**result)


if (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")


if DIST_DIR.exists():
    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(DIST_DIR / "index.html")


    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        candidate = DIST_DIR / full_path
        if full_path and candidate.exists() and candidate.is_file():
            return FileResponse(candidate)

        return FileResponse(DIST_DIR / "index.html")
