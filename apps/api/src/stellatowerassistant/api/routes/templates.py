from __future__ import annotations

from fastapi import APIRouter

from ..schemas.templates import TemplatesResponse
from ...core.services.template_service import list_templates

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=TemplatesResponse)
def get_templates() -> TemplatesResponse:
    return TemplatesResponse(items=list_templates())
