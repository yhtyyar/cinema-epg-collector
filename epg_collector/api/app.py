from __future__ import annotations

import asyncio
import logging
import time
from typing import List

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from epg_collector.api.routes import router as movies_router
from epg_collector.api.dependencies import get_settings, get_cache


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Cinema EPG Collector API",
        version="0.1.0",
        description="REST API для доступа к объединённым данным фильмов из EPG/КиноПоиск",
    )

    # CORS
    origins: List[str] = settings.api_cors_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging middleware
    logger = logging.getLogger("api")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info("%s %s -> %s in %.2fms", request.method, request.url.path, response.status_code, duration)
        return response

    # Error handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": "Invalid request", "errors": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logging.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    # Static files for posters and other data
    app.mount("/static", StaticFiles(directory="data"), name="static")

    # Routers
    app.include_router(movies_router)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    # Optional: auto-run data pipeline on startup (in background)
    async def _run_pipeline_bg() -> None:
        try:
            # Import locally to avoid circular deps on app import
            from epg_collector.cli import run_all as run_pipeline

            # Run sync pipeline without blocking the event loop
            await asyncio.to_thread(run_pipeline)
            logger.info("Data pipeline completed successfully")
        except Exception as exc:
            logger.exception("Data pipeline failed: %s", exc)
        finally:
            try:
                cache = get_cache(settings)
                cache.clear()
                logger.info("API cache cleared after pipeline")
            except Exception as e:
                logger.exception("Failed to clear API cache after pipeline: %s", e)

    @app.on_event("startup")
    async def _schedule_pipeline_on_startup() -> None:
        if settings.auto_run_pipeline:
            logger.info("AUTO_RUN_PIPELINE is enabled; scheduling pipeline on startup")
            asyncio.create_task(_run_pipeline_bg())

    return app


app = create_app()
