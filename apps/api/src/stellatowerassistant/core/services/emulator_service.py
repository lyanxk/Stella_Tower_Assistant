from __future__ import annotations

import base64
from datetime import datetime, timezone

import cv2

from ..automation.vision import capture_emulator, get_emulator_window


def get_window_status() -> dict[str, object]:
    window = get_emulator_window()
    if window is None:
        return {"connected": False, "title": None}

    return {
        "connected": True,
        "title": window.title,
        "left": window.left,
        "top": window.top,
        "width": window.width,
        "height": window.height,
    }


def capture_preview() -> dict[str, object]:
    image, (_, _, width, height) = capture_emulator()
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Failed to encode emulator screenshot.")

    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "width": width,
        "height": height,
        "image_base64": base64.b64encode(encoded.tobytes()).decode("ascii"),
    }
