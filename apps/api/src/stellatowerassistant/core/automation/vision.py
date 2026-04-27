from __future__ import annotations

import time
from functools import lru_cache
from typing import Optional

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw

from ..config.settings import (
    EMULATOR_TITLE_KEYWORDS,
    IMAGE_MATCH_THRESHOLD,
    MATCH_DEDUP_DISTANCE,
    RESOURCE_DIR,
    TEMPLATES,
)
from ..runtime.state import state

Point = tuple[int, int]
WindowRect = tuple[int, int, int, int]


@lru_cache(maxsize=None)
def load_template(name: str) -> Optional[np.ndarray]:
    filename = TEMPLATES.get(name)
    if filename is None:
        return None

    path = RESOURCE_DIR / filename
    if not path.is_file():
        return None

    template = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if template is None or template.size == 0:
        return None

    return template


def require_template(name: str) -> np.ndarray:
    template = load_template(name)
    if template is None:
        raise ValueError(f"Template {name} not found in resources.")
    return template


def get_emulator_window() -> Optional[gw.Win32Window]:
    for window in gw.getAllWindows():
        title = window.title.lower()
        if any(keyword in title for keyword in EMULATOR_TITLE_KEYWORDS):
            return window
    return None


def capture_emulator() -> tuple[np.ndarray, WindowRect]:
    state.check_pause_and_running()

    window = get_emulator_window()
    if window is None:
        raise RuntimeError("MuMu window not found. Ensure the emulator is running.")

    left, top, width, height = window.left, window.top, window.width, window.height
    if width <= 0 or height <= 0:
        window.restore()
        state.check_pause_and_running()
        time.sleep(0.5)
        left, top, width, height = window.left, window.top, window.width, window.height

    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return image, (left, top, width, height)


def match_template(
    source: np.ndarray,
    template: np.ndarray,
    threshold: float = IMAGE_MATCH_THRESHOLD,
) -> Optional[Point]:
    result = match_template_scores(source, template)
    if result.size == 0:
        return None

    _, max_value, _, max_location = cv2.minMaxLoc(result)
    if max_value < threshold:
        return None

    template_height, template_width = template.shape[:2]
    x, y = max_location
    return x + template_width // 2, y + template_height // 2


def match_template_scores(source: np.ndarray, template: np.ndarray) -> np.ndarray:
    if source is None or template is None:
        return np.empty((0, 0), dtype=np.float32)

    source_height, source_width = source.shape[:2]
    template_height, template_width = template.shape[:2]
    if source_height < template_height or source_width < template_width:
        return np.empty((0, 0), dtype=np.float32)

    if source.dtype != template.dtype or source.dtype not in (np.uint8, np.float32):
        source = source.astype(np.float32, copy=False)
        template = template.astype(np.float32, copy=False)

    return cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)


def find_all_matches(
    source: np.ndarray,
    template: np.ndarray,
    threshold: float,
) -> list[Point]:
    result = match_template_scores(source, template)
    if result.size == 0:
        return []

    ys, xs = np.where(result >= threshold)
    if len(xs) == 0:
        return []

    template_height, template_width = template.shape[:2]
    centers = [(int(x + template_width // 2), int(y + template_height // 2)) for x, y in zip(xs, ys)]
    centers.sort(key=lambda point: (point[1], point[0]))

    filtered: list[Point] = []
    for candidate in centers:
        if any(abs(candidate[0] - x) + abs(candidate[1] - y) < MATCH_DEDUP_DISTANCE for x, y in filtered):
            continue
        filtered.append(candidate)

    return filtered
