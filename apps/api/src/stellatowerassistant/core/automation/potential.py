from __future__ import annotations

import time

from ..config.settings import (
    IMAGE_MATCH_THRESHOLD,
    POTENTIAL_REFRESH_LIMIT,
    POTENTIAL_REFRESH_WAIT_SECONDS,
    SELECT_CONFIRM_TIMEOUT,
    SELECT_MATCH_THRESHOLD,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .actions import click_match_center
from .vision import WindowRect, capture_emulator, load_template, match_template


def has_potential_prompt(image) -> bool:
    if is_shop_purchase_page(image):
        return False

    return _has_template(image, "refresh") or _has_template(image, "select_confirm", threshold=SELECT_MATCH_THRESHOLD)


def is_shop_purchase_page(image) -> bool:
    return _has_template(image, "back")


def handle_potential_selection(max_refreshes: int = POTENTIAL_REFRESH_LIMIT, timeout: float = 8.0) -> bool:
    emit_log("Handling potential selection...", scope="potential")
    refresh_count = 0
    start_time = time.time()

    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        if is_shop_purchase_page(image):
            emit_log("Shop purchase page detected before potential decision; leaving potential flow.", scope="potential")
            return False

        refresh_match = _match(image, "refresh")
        if not refresh_match:
            if _click_take_if_present(image, window_rect):
                return True
            time.sleep(0.2)
            continue

        if _click_thumb_if_present(image, window_rect):
            return True

        if refresh_count >= max_refreshes:
            emit_log("Potential refresh limit reached, taking current option if available.", scope="potential")
            if _click_take_when_available(timeout=SELECT_CONFIRM_TIMEOUT):
                return True
            return False

        emit_log(f"Refreshing potential options ({refresh_count + 1}/{max_refreshes})", scope="potential")
        time.sleep(POTENTIAL_REFRESH_WAIT_SECONDS)
        image, window_rect = capture_emulator()
        if is_shop_purchase_page(image):
            emit_log("Shop purchase page detected before potential refresh; leaving potential flow.", scope="potential")
            return False

        if _click_thumb_if_present(image, window_rect):
            return True

        refresh_match = _match(image, "refresh")
        if not refresh_match:
            if _click_take_if_present(image, window_rect):
                return True
            continue

        click_match_center(refresh_match, window_rect, delay=0.5)
        refresh_count += 1

    return False


def _click_thumb_if_present(image, window_rect: WindowRect) -> bool:
    thumb_match = _match(image, "select", threshold=SELECT_MATCH_THRESHOLD)
    if not thumb_match:
        return False

    emit_log(f"Potential thumb matched at {thumb_match}", scope="potential")
    click_match_center(thumb_match, window_rect, delay=0.3)
    return _click_take_when_available(timeout=SELECT_CONFIRM_TIMEOUT)


def _click_take_if_present(image, window_rect: WindowRect) -> bool:
    take_match = _match(image, "select_confirm", threshold=SELECT_MATCH_THRESHOLD)
    if not take_match:
        return False

    emit_log(f"Take potential matched at {take_match}", scope="potential")
    click_match_center(take_match, window_rect, delay=0.3)
    return True


def _click_take_when_available(timeout: float) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        if _click_take_if_present(image, window_rect):
            return True
        time.sleep(0.2)
    return False


def _has_template(image, template_name: str, threshold: float = IMAGE_MATCH_THRESHOLD) -> bool:
    return _match(image, template_name, threshold=threshold) is not None


def _match(image, template_name: str, threshold: float = IMAGE_MATCH_THRESHOLD):
    template = load_template(template_name)
    if template is None:
        return None

    return match_template(image, template, threshold=threshold)
