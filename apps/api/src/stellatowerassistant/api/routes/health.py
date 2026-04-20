from __future__ import annotations

from fastapi import APIRouter

from ...core.services.automation_service import automation_service
from ...core.services.emulator_service import get_window_status

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, object]:
    return {
        "ok": True,
        "automation": automation_service.get_status(),
        "emulator": get_window_status(),
    }
