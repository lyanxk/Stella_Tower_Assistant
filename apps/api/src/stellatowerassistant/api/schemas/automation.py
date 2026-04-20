from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ActionResponse(BaseModel):
    ok: bool
    message: str


class AutomationStatus(BaseModel):
    is_running: bool
    is_paused: bool
    skip_initial_wait: bool
    current_run: int
    max_runs: int
    last_error: str | None = None
    last_message: str
    started_at: str | None = None
    finished_at: str | None = None
    thread_alive: bool


class AutomationLogEntry(BaseModel):
    id: str
    timestamp: str
    level: str
    scope: str
    message: str
    event_type: str = "log"
    payload: dict[str, Any] = Field(default_factory=dict)


class LogsResponse(BaseModel):
    items: list[AutomationLogEntry]
