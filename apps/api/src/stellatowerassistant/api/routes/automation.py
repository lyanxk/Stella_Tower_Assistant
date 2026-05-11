from __future__ import annotations

from fastapi import APIRouter, Query

from ..schemas.automation import ActionResponse, AutomationStatus, LogsResponse
from ...core.services.automation_service import automation_service

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.get("/status", response_model=AutomationStatus)
def get_status() -> dict[str, object]:
    return automation_service.get_status()


@router.get("/logs", response_model=LogsResponse)
def get_logs(limit: int = Query(default=100, ge=1, le=300)) -> dict[str, object]:
    return {"items": automation_service.get_logs(limit)}


@router.post("/start", response_model=ActionResponse)
def start() -> ActionResponse:
    ok, message = automation_service.start()
    return ActionResponse(ok=ok, message=message)


@router.post("/pause", response_model=ActionResponse)
def pause() -> ActionResponse:
    ok, message = automation_service.pause()
    return ActionResponse(ok=ok, message=message)


@router.post("/resume", response_model=ActionResponse)
def resume() -> ActionResponse:
    ok, message = automation_service.resume()
    return ActionResponse(ok=ok, message=message)


@router.post("/stop", response_model=ActionResponse)
def stop() -> ActionResponse:
    ok, message = automation_service.stop()
    return ActionResponse(ok=ok, message=message)
