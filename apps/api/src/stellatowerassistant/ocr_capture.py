from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path
from typing import Literal

import cv2
import keyboard
import numpy as np
import pyautogui

if __package__ in (None, ""):
    SRC_DIR = Path(__file__).resolve().parents[1]
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    from stellatowerassistant.core.automation.ocr import recognize_digit_sequences
    from stellatowerassistant.core.automation.vision import get_emulator_window
else:
    from .core.automation.ocr import recognize_digit_sequences
    from .core.automation.vision import get_emulator_window

CaptureMode = Literal["auto", "screen", "emulator"]
OcrVariant = Literal["auto", "small", "elevator"]

DEFAULT_CAPTURE_HOTKEY = "f8"
DEFAULT_QUIT_HOTKEY = "esc"
CAPTURE_DEBOUNCE_SECONDS = 0.2


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="stella-tower-ocr",
        description="Capture a screenshot on hotkey press and print recognized digit groups.",
    )
    parser.add_argument(
        "--variant",
        choices=("auto", "small", "elevator"),
        default="auto",
        help="Which digit template set to use. Default: auto.",
    )
    parser.add_argument(
        "--capture-mode",
        choices=("auto", "screen", "emulator"),
        default="auto",
        help="Capture the emulator window when available, or the full screen. Default: auto.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.98,
        help="Template match threshold. Higher values reduce false positives. Default: 0.98.",
    )
    parser.add_argument(
        "--capture-hotkey",
        default=DEFAULT_CAPTURE_HOTKEY,
        help=f"Hotkey used to capture a screenshot. Default: {DEFAULT_CAPTURE_HOTKEY}.",
    )
    parser.add_argument(
        "--quit-hotkey",
        default=DEFAULT_QUIT_HOTKEY,
        help=f"Hotkey used to quit the tool. Default: {DEFAULT_QUIT_HOTKEY}.",
    )
    args = parser.parse_args()

    run_ocr_capture_console(
        variant=args.variant,
        capture_mode=args.capture_mode,
        threshold=args.threshold,
        capture_hotkey=args.capture_hotkey,
        quit_hotkey=args.quit_hotkey,
    )


def run_ocr_capture_console(
    variant: OcrVariant = "auto",
    capture_mode: CaptureMode = "auto",
    threshold: float = 0.98,
    capture_hotkey: str = DEFAULT_CAPTURE_HOTKEY,
    quit_hotkey: str = DEFAULT_QUIT_HOTKEY,
) -> None:
    capture_lock = threading.Lock()
    last_capture_time = 0.0

    def handle_capture() -> None:
        nonlocal last_capture_time

        now = time.monotonic()
        if now - last_capture_time < CAPTURE_DEBOUNCE_SECONDS:
            return

        if not capture_lock.acquire(blocking=False):
            return

        try:
            image = capture_screenshot_image(capture_mode)
            sequences = recognize_sequences_for_capture(image, variant=variant, threshold=threshold)
            print(",".join(sequences), flush=True)
            last_capture_time = time.monotonic()
        except Exception as exc:
            print(f"[ocr-capture] {exc}", flush=True)
            last_capture_time = time.monotonic()
        finally:
            capture_lock.release()

    print(f"Press {capture_hotkey} to capture a screenshot.", flush=True)
    print(f"Press {quit_hotkey} to quit.", flush=True)

    hotkey_handle = keyboard.add_hotkey(capture_hotkey, handle_capture, suppress=False)
    try:
        keyboard.wait(quit_hotkey)
    finally:
        keyboard.remove_hotkey(hotkey_handle)


def capture_screenshot_image(capture_mode: CaptureMode) -> np.ndarray:
    if capture_mode in ("auto", "emulator"):
        emulator_image = capture_emulator_window_image()
        if emulator_image is not None:
            return emulator_image
        if capture_mode == "emulator":
            raise RuntimeError("Emulator window not found.")

    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def capture_emulator_window_image() -> np.ndarray | None:
    window = get_emulator_window()
    if window is None:
        return None

    left, top, width, height = window.left, window.top, window.width, window.height
    if width <= 0 or height <= 0:
        return None

    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def recognize_sequences_for_capture(
    image: np.ndarray,
    variant: OcrVariant,
    threshold: float,
) -> list[str]:
    if variant != "auto":
        return recognize_digit_sequences(image, variant=variant, threshold=threshold)

    results_by_variant = {
        "small": recognize_digit_sequences(image, variant="small", threshold=threshold),
        "elevator": recognize_digit_sequences(image, variant="elevator", threshold=threshold),
    }
    return choose_best_variant_result(results_by_variant)


def choose_best_variant_result(results_by_variant: dict[str, list[str]]) -> list[str]:
    best_result: list[str] = []
    best_score = (-1, 0, -1)

    for variant, result in results_by_variant.items():
        score = (
            sum(len(group) for group in result),
            -len(result),
            1 if variant == "elevator" else 0,
        )
        if score > best_score:
            best_score = score
            best_result = result

    return best_result


if __name__ == "__main__":
    main()
