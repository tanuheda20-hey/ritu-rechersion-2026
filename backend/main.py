"""
Ritu — cycle-aware symptom intelligence.
Built for recHERsion 2026 (ACM-W NITK Surathkal) · Problem Statement 1: Women's Healthcare.

FastAPI + SQLite. `make dev` and it runs.
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from db import init_db, DB_PATH
from routers import logs as logs_router
from services.insights import DISCLAIMER

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
log = logging.getLogger("ritu")

APP_TITLE = os.getenv("APP_TITLE", "Ritu — Cycle-Aware Symptom Intelligence")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log.info("database ready at %s", DB_PATH)
    yield
    log.info("shutting down")


app = FastAPI(
    title=APP_TITLE,
    version="1.0.0",
    description=(
        "Turns daily symptom logs into patterns a doctor can act on. "
        "Built for recHERsion 2026, Problem Statement 1 — Women's Healthcare.\n\n"
        "⚠️ " + DISCLAIMER
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.exception("unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


@app.middleware("http")
async def timing(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - t0) * 1000:.1f}ms"
    return response


@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": APP_TITLE, "version": "1.0.0"}


app.include_router(logs_router.router, prefix="/api")


# Serve the built frontend in production — one deploy, one URL.
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
