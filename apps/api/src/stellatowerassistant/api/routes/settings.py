from __future__ import annotations

from fastapi import APIRouter

from ..schemas.settings import SettingsResponse
from ...core.config.settings import (
    API_HOST,
    API_PORT,
    EMULATOR_TITLE_KEYWORDS,
    FAST_CLICK_DELAY,
    FAST_CLICK_DURATION,
    HUNDRED_MATCH_THRESHOLD,
    IMAGE_MATCH_THRESHOLD,
    MATCH_POLL_INTERVAL,
    MAX_RUNS,
    MAX_SHOPS_PER_RUN,
    RESOURCE_DIR,
    SELECT_CONFIRM_TIMEOUT,
    SELECT_MATCH_THRESHOLD,
    SOLD_OUT_MATCH_THRESHOLD,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    return SettingsResponse(
        api_host=API_HOST,
        api_port=API_PORT,
        resource_dir=str(RESOURCE_DIR),
        emulator_keywords=list(EMULATOR_TITLE_KEYWORDS),
        thresholds={
            "image_match": IMAGE_MATCH_THRESHOLD,
            "select_match": SELECT_MATCH_THRESHOLD,
            "hundred_match": HUNDRED_MATCH_THRESHOLD,
            "sold_out_match": SOLD_OUT_MATCH_THRESHOLD,
        },
        timing={
            "match_poll_interval": MATCH_POLL_INTERVAL,
            "select_confirm_timeout": SELECT_CONFIRM_TIMEOUT,
            "fast_click_delay": FAST_CLICK_DELAY,
            "fast_click_duration": FAST_CLICK_DURATION,
        },
        limits={
            "max_runs": MAX_RUNS,
            "max_shops_per_run": MAX_SHOPS_PER_RUN,
        },
    )
