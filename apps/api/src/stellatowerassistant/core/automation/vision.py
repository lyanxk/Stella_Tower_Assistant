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


def _ensure_channel_axis(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image[:, :, None]
    return image


def _window_sums(image: np.ndarray, window_height: int, window_width: int) -> np.ndarray:
    integral = np.pad(image, ((1, 0), (1, 0), (0, 0)), mode="constant").cumsum(axis=0).cumsum(axis=1)
    return (
        integral[window_height:, window_width:]
        - integral[:-window_height, window_width:]
        - integral[window_height:, :-window_width]
        + integral[:-window_height, :-window_width]
    )


def _match_template_coeff_normed(source: np.ndarray, template: np.ndarray) -> np.ndarray:
    source_3d = _ensure_channel_axis(source)
    template_3d = _ensure_channel_axis(template)

    source_height, source_width = source_3d.shape[:2]
    template_height, template_width = template_3d.shape[:2]
    if source_height < template_height or source_width < template_width:
        return np.empty((0, 0), dtype=np.float32)

    source_float = source_3d.astype(np.float32)
    template_float = template_3d.astype(np.float32)

    template_mean = template_float.mean(axis=(0, 1), keepdims=True)
    template_centered = template_float - template_mean
    template_energy = float(np.square(template_centered, dtype=np.float64).sum())

    out_height = source_height - template_height + 1
    out_width = source_width - template_width + 1
    if template_energy <= 1e-12:
        return np.zeros((out_height, out_width), dtype=np.float32)

    numerator = np.zeros((out_height, out_width), dtype=np.float32)
    for channel in range(source_float.shape[2]):
        channel_response = cv2.filter2D(
            source_float[:, :, channel],
            ddepth=cv2.CV_32F,
            kernel=template_centered[:, :, channel],
            anchor=(0, 0),
            borderType=cv2.BORDER_CONSTANT,
        )
        numerator += channel_response[:out_height, :out_width]

    source_square = np.square(source_float, dtype=np.float64)
    source_sums = _window_sums(source_float.astype(np.float64), template_height, template_width)
    source_square_sums = _window_sums(source_square, template_height, template_width)
    window_area = float(template_height * template_width)
    source_energy = np.maximum(source_square_sums - np.square(source_sums) / window_area, 0.0).sum(axis=2)

    denominator = np.sqrt(template_energy * source_energy)
    scores = np.zeros((out_height, out_width), dtype=np.float32)
    np.divide(numerator, denominator, out=scores, where=denominator > 1e-12)
    return np.clip(scores, -1.0, 1.0)


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
    if source is None or template is None:
        return None

    result = _match_template_coeff_normed(source, template)
    if result.size == 0:
        return None

    _, max_value, _, max_location = cv2.minMaxLoc(result)
    if max_value < threshold:
        return None

    template_height, template_width = template.shape[:2]
    x, y = max_location
    return x + template_width // 2, y + template_height // 2


def find_all_matches(
    source: np.ndarray,
    template: np.ndarray,
    threshold: float,
) -> list[Point]:
    if source is None or template is None:
        return []

    result = _match_template_coeff_normed(source, template)
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
