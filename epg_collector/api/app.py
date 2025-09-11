from __future__ import annotations

import asyncio
import logging
import time
from typing import List

from fastapi import FastAPI, Request, BackgroundTasks
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

    @app.get("/api/data-status")
    async def data_status():
        """Возвращает подробную информацию о состоянии данных EPG и постеров."""
        from epg_collector.data_validator import get_data_status, validate_data_freshness
        
        status = get_data_status()
        needs_update, reason = validate_data_freshness()
        
        return {
            "needs_update": needs_update,
            "reason": reason,
            "details": status,
            "timestamp": time.time()
        }

    async def _run_pipeline_bg() -> None:
        """Фоновая задача для запуска пайплайна сбора данных."""
        try:
            # Import locally to avoid circular deps on app import
            from epg_collector.cli import run_all as run_pipeline
            from epg_collector.data_validator import cleanup_old_artifacts

            logger.info("Очистка старых артефактов перед запуском пайплайна...")
            cleanup_old_artifacts()
            
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

    @app.post("/api/collect-data")
    async def collect_data(background_tasks: BackgroundTasks):
        """Запустить сбор данных в фоновом режиме."""
        background_tasks.add_task(_run_pipeline_bg)
        return {"message": "Data collection started in background"}

    @app.on_event("startup")
    async def _schedule_pipeline_on_startup() -> None:
        from epg_collector.data_validator import should_run_pipeline, get_data_status
        
        # If AUTO_RUN_PIPELINE is explicitly set to false, don't run pipeline at startup
        if not settings.auto_run_pipeline:
            logger.info("AUTO_RUN_PIPELINE is false, skipping pipeline at startup")
            # Логируем текущий статус данных
            data_status = get_data_status()
            logger.info(f"Статус данных: {data_status}")
            return
        
        # Проверяем актуальность данных
        should_run, reason = should_run_pipeline(
            force_run=settings.auto_run_pipeline,
            max_age_hours=24
        )
        
        if should_run:
            logger.info(f"Запуск пайплайна: {reason}")
            # Run in background without blocking startup
            asyncio.create_task(_run_pipeline_bg())
        else:
            logger.info(f"Пайплайн не требуется: {reason}")
            
        # Логируем текущий статус данных
        data_status = get_data_status()
        logger.info(f"Статус данных: {data_status}")

    return app


app = create_app()