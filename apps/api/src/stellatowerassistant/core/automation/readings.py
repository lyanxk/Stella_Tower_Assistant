from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from ..config.settings import (
    OCR_CURRENT_GOLD_FALLBACK_THRESHOLD,
    OCR_CURRENT_GOLD_REGION,
    OCR_CURRENT_GOLD_THRESHOLD,
    OCR_OBSERVE_INTERVAL,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .ocr import DigitSequence, recognize_digit_sequence_groups

RegionRatio = tuple[float, float, float, float]


@dataclass(frozen=True)
class RunReading:
    current_gold: int | None = None
    gold_candidates: tuple[str, ...] = field(default_factory=tuple)


_last_reading = RunReading()
_last_observed_at = 0.0


def reset_run_reading_observer() -> None:
    global _last_observed_at, _last_reading

    _last_reading = RunReading()
    _last_observed_at = 0.0


def observe_run_reading(image: np.ndarray, *, force: bool = False) -> RunReading:
    global _last_observed_at, _last_reading

    now = time.monotonic()
    if not force and now - _last_observed_at < OCR_OBSERVE_INTERVAL:
        return _last_reading

    _last_observed_at = now
    reading = read_run_reading(image)
    if reading == _last_reading:
        return reading

    _last_reading = reading
    state.mark_ocr_reading(current_gold=reading.current_gold)
    emit_log(
        _format_reading_message(reading),
        scope="ocr",
        payload={
            "current_gold": reading.current_gold,
            "gold_candidates": list(reading.gold_candidates),
        },
        event_type="ocr_reading",
    )
    return reading


def read_run_reading(image: np.ndarray) -> RunReading:
    gold_sequences = _read_digit_sequences(
        image,
        region=OCR_CURRENT_GOLD_REGION,
        variant="small",
        threshold=OCR_CURRENT_GOLD_FALLBACK_THRESHOLD,
    )
    current_gold = _choose_gold(gold_sequences, preferred_threshold=OCR_CURRENT_GOLD_THRESHOLD)

    return RunReading(
        current_gold=current_gold,
        gold_candidates=tuple(sequence.text for sequence in gold_sequences),
    )


def _read_digit_sequences(
    image: np.ndarray,
    *,
    region: RegionRatio,
    variant: str,
    threshold: float,
) -> list[DigitSequence]:
    cropped = _crop_ratio(image, region)
    if cropped.size == 0:
        return []

    return recognize_digit_sequence_groups(cropped, variant=variant, threshold=threshold)


def _crop_ratio(image: np.ndarray, region: RegionRatio) -> np.ndarray:
    height, width = image.shape[:2]
    x_ratio, y_ratio, width_ratio, height_ratio = region
    left = _clamp(int(round(width * x_ratio)), 0, width)
    top = _clamp(int(round(height * y_ratio)), 0, height)
    right = _clamp(int(round(width * (x_ratio + width_ratio))), left, width)
    bottom = _clamp(int(round(height * (y_ratio + height_ratio))), top, height)
    return image[top:bottom, left:right]


def _choose_gold(sequences: list[DigitSequence], *, preferred_threshold: float) -> int | None:
    candidates = [(value, sequence) for sequence in sequences if (value := _parse_int(sequence.text)) is not None]
    if not candidates:
        return None

    preferred_candidates = [(value, sequence) for value, sequence in candidates if sequence.score >= preferred_threshold]
    if preferred_candidates:
        candidates = preferred_candidates

    value, _ = max(candidates, key=lambda item: (len(item[1].text), item[1].score, -item[1].top, item[1].left))
    return value


def _parse_int(text: str) -> int | None:
    if not text.isdigit():
        return None

    return int(text)


def _format_reading_message(reading: RunReading) -> str:
    gold = reading.current_gold if reading.current_gold is not None else "?"
    return f"OCR reading: gold={gold}"


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))
