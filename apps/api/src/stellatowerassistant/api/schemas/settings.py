from __future__ import annotations

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    api_host: str
    api_port: int
    resource_dir: str
    emulator_keywords: list[str]
    thresholds: dict[str, float]
    timing: dict[str, float]
    limits: dict[str, int]
