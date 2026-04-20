from __future__ import annotations

from pydantic import BaseModel


class TemplateInfo(BaseModel):
    key: str
    filename: str
    path: str
    exists: bool


class TemplatesResponse(BaseModel):
    items: list[TemplateInfo]


class ScreenshotResponse(BaseModel):
    captured_at: str
    width: int
    height: int
    image_base64: str
