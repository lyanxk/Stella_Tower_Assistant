from __future__ import annotations

import time

import pyautogui

from ..config.settings import (
    BLANK_CLICK_X_OFFSET,
    FALLBACK_CHOICE_X_RATIO,
    FAST_CLICK_DELAY,
    FAST_CLICK_DURATION,
    FAST_CLICK_X_OFFSET,
    IMAGE_MATCH_THRESHOLD,
    INITIAL_WAIT_TEMPLATES,
    MATCH_POLL_INTERVAL,
    SELECT_CONFIRM_TIMEOUT,
    SELECT_MATCH_THRESHOLD,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .vision import Point, WindowRect, capture_emulator, load_template, match_template, require_template


def click_match_center(match: Point, window_rect: WindowRect, delay: float = 0.0) -> None:
    state.check_pause_and_running()
    pyautogui.click(window_rect[0] + match[0], window_rect[1] + match[1])
    if delay:
        time.sleep(delay)


def click_relative(offset_x: int, offset_y: int, window_rect: WindowRect, delay: float = 0.0) -> None:
    state.check_pause_and_running()
    pyautogui.click(window_rect[0] + offset_x, window_rect[1] + offset_y)
    if delay:
        time.sleep(delay)


def click_blank(window_rect: WindowRect, times: int = 1, delay: float = 0.0) -> None:
    left, top, _, height = window_rect
    click_point = (left + BLANK_CLICK_X_OFFSET, top + height // 2)

    for _ in range(times):
        state.check_pause_and_running()
        pyautogui.click(*click_point)
        if delay:
            time.sleep(delay)


def wait_and_click(
    template_name: str,
    timeout: float = 30.0,
    threshold: float = IMAGE_MATCH_THRESHOLD,
) -> bool:
    template = require_template(template_name)
    start_time = time.time()
    is_initial_wait = template_name in INITIAL_WAIT_TEMPLATES

    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        if is_initial_wait and state.skip_initial_wait:
            emit_log(f"[Skip] Skip waiting for {template_name}", scope="automation")
            return False

        image, window_rect = capture_emulator()
        match = match_template(image, template, threshold)
        if match:
            click_match_center(match, window_rect)
            return True

        time.sleep(MATCH_POLL_INTERVAL)

    emit_log(f"[Timeout] {template_name} not found in {timeout} seconds", level="warning", scope="automation")
    return False


def continuous_fast_click(delay: float = FAST_CLICK_DELAY, duration: float = FAST_CLICK_DURATION) -> None:
    _, window_rect = capture_emulator()
    left, top, _, height = window_rect
    click_x = left + FAST_CLICK_X_OFFSET
    click_y = top + height // 2
    end_time = time.time() + duration

    while time.time() < end_time:
        state.check_pause_and_running()
        pyautogui.click(click_x, click_y)
        time.sleep(delay)


def click_template_if_present(
    image,
    window_rect: WindowRect,
    template_name: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
    delay: float = 0.0,
) -> bool:
    template = load_template(template_name)
    if template is None:
        return False

    match = match_template(image, template, threshold)
    if not match:
        return False

    click_match_center(match, window_rect, delay=delay)
    return True


def select_choice_or_first() -> None:
    select_template = load_template("select")
    choice_template = load_template("choice")
    confirm_template = load_template("select_confirm")

    image, window_rect = capture_emulator()

    select_match = match_template(image, select_template, threshold=SELECT_MATCH_THRESHOLD) if select_template is not None else None
    if select_match:
        emit_log(f"[Debug] select matched at {select_match}", scope="automation")
        click_match_center(select_match, window_rect, delay=0.3)

        start_time = time.time()
        while time.time() - start_time < SELECT_CONFIRM_TIMEOUT:
            state.check_pause_and_running()
            confirm_image, confirm_rect = capture_emulator()
            confirm_match = (
                match_template(confirm_image, confirm_template, threshold=SELECT_MATCH_THRESHOLD)
                if confirm_template is not None
                else None
            )
            if confirm_match:
                emit_log(f"[Debug] select_confirm matched at {confirm_match}", scope="automation")
                click_match_center(confirm_match, confirm_rect)
                return
            time.sleep(0.2)

        return

    choice_match = match_template(image, choice_template, threshold=IMAGE_MATCH_THRESHOLD) if choice_template is not None else None
    if choice_match:
        emit_log(f"[Debug] choice matched at {choice_match}", scope="automation")
        click_match_center(choice_match, window_rect)
        return

    left, top, width, height = window_rect
    fallback_x = left + int(width * FALLBACK_CHOICE_X_RATIO)
    fallback_y = top + height // 2
    emit_log(f"[Debug] fallback click at ({fallback_x}, {fallback_y})", scope="automation")
    state.check_pause_and_running()
    pyautogui.click(fallback_x, fallback_y)
