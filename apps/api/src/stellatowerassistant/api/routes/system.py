from __future__ import annotations

import os
import time

from fastapi import APIRouter, BackgroundTasks

from ..schemas.automation import ActionResponse
from ...core.runtime.events import emit_log
from ...core.services.automation_service import automation_service

router = APIRouter(prefix="/api/system", tags=["system"])


def _exit_process() -> None:
    time.sleep(0.3)
    os._exit(0)


@router.post("/exit", response_model=ActionResponse)
def exit_application(background_tasks: BackgroundTasks) -> ActionResponse:
    automation_service.stop()
    emit_log("Exit requested from frontend.", scope="service", event_type="status")
    background_tasks.add_task(_exit_process)
    return ActionResponse(ok=True, message="Exit requested.")
