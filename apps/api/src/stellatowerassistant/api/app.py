from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core.config.settings import CORS_ORIGINS
from .routes import automation_router, emulator_router, health_router, settings_router, system_router, templates_router
from .ws import events_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Stella Tower Assistant API",
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(CORS_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(automation_router)
    application.include_router(settings_router)
    application.include_router(templates_router)
    application.include_router(emulator_router)
    application.include_router(system_router)
    application.include_router(events_router)
    return application


app = create_app()
