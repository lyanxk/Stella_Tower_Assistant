from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.templates import ScreenshotResponse
from ...core.services.emulator_service import capture_preview, get_window_status

router = APIRouter(prefix="/api/emulator", tags=["emulator"])


@router.get("/window")
def get_window() -> dict[str, object]:
    return get_window_status()


@router.get("/screenshot", response_model=ScreenshotResponse)
def get_screenshot() -> ScreenshotResponse:
    try:
        return ScreenshotResponse(**capture_preview())
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
