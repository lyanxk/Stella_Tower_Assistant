from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Literal

import cv2
import numpy as np

OcrVariant = Literal["small", "elevator"]

DEFAULT_DIGIT_MATCH_THRESHOLD = 0.80
DEFAULT_DIGIT_MAX_GAP_RATIO = 1.5
DEFAULT_ROW_ALIGNMENT_RATIO = 0.6

_DIGIT_RE = re.compile(r"\d+")
_NON_DIGIT_RE = re.compile(r"\D+")
_OCR_UPSCALE_FACTOR = 2.0
_OCR_BORDER_PIXELS = 12


@dataclass(frozen=True)
class DigitSequence:
    text: str
    score: float
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


@dataclass(frozen=True)
class _OcrLine:
    text: str
    score: float
    box: np.ndarray | None


def recognize_digit_sequences(
    source: np.ndarray,
    variant: OcrVariant = "small",
    threshold: float = DEFAULT_DIGIT_MATCH_THRESHOLD,
    max_gap_ratio: float = DEFAULT_DIGIT_MAX_GAP_RATIO,
    row_alignment_ratio: float = DEFAULT_ROW_ALIGNMENT_RATIO,
) -> list[str]:
    return [
        sequence.text
        for sequence in recognize_digit_sequence_groups(
            source,
            variant=variant,
            threshold=threshold,
            max_gap_ratio=max_gap_ratio,
            row_alignment_ratio=row_alignment_ratio,
        )
    ]


def recognize_digit_sequence_groups(
    source: np.ndarray,
    variant: OcrVariant = "small",
    threshold: float = DEFAULT_DIGIT_MATCH_THRESHOLD,
    max_gap_ratio: float = DEFAULT_DIGIT_MAX_GAP_RATIO,
    row_alignment_ratio: float = DEFAULT_ROW_ALIGNMENT_RATIO,
) -> list[DigitSequence]:
    del variant, max_gap_ratio, row_alignment_ratio

    if source is None or source.size == 0:
        return []

    result = _run_maa_style_ocr(_prepare_ocr_source(source))
    sequences = [
        sequence
        for line in _iter_ocr_lines(result)
        if (sequence := _build_digit_sequence(line)) is not None and sequence.score >= threshold
    ]

    if not sequences:
        inverted_result = _run_maa_style_ocr(_prepare_ocr_source(source, invert=True))
        sequences = [
            sequence
            for line in _iter_ocr_lines(inverted_result)
            if (sequence := _build_digit_sequence(line)) is not None and sequence.score >= threshold
        ]

    sequences.sort(key=lambda item: (item.top, item.left))
    return sequences


@lru_cache(maxsize=1)
def _load_ocr_engine() -> Any:
    try:
        from rapidocr import RapidOCR
    except ImportError as exc:
        raise RuntimeError(
            "RapidOCR is required for OCR. Install backend dependencies with "
            "`python -m pip install -r apps/api/requirements.txt`."
        ) from exc

    return RapidOCR()


def _run_maa_style_ocr(source: np.ndarray) -> Any:
    engine = _load_ocr_engine()
    return engine(source, use_det=True, use_cls=True, use_rec=True)


def _prepare_ocr_source(source: np.ndarray, *, invert: bool = False) -> np.ndarray:
    image = _as_uint8_image(source)
    if invert:
        image = cv2.bitwise_not(image)

    if _OCR_UPSCALE_FACTOR != 1.0:
        image = cv2.resize(
            image,
            None,
            fx=_OCR_UPSCALE_FACTOR,
            fy=_OCR_UPSCALE_FACTOR,
            interpolation=cv2.INTER_CUBIC,
        )

    if _OCR_BORDER_PIXELS > 0:
        border_color = (255, 255, 255) if invert else (0, 0, 0)
        image = cv2.copyMakeBorder(
            image,
            _OCR_BORDER_PIXELS,
            _OCR_BORDER_PIXELS,
            _OCR_BORDER_PIXELS,
            _OCR_BORDER_PIXELS,
            cv2.BORDER_CONSTANT,
            value=border_color,
        )

    return image


def _as_uint8_image(source: np.ndarray) -> np.ndarray:
    image = source
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)

    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image


def _iter_ocr_lines(result: Any) -> list[_OcrLine]:
    txts = getattr(result, "txts", None)
    if txts is not None:
        boxes = getattr(result, "boxes", None)
        scores = getattr(result, "scores", None)
        if scores is None:
            scores = ()
        return [
            _OcrLine(
                text=str(text),
                score=_score_at(scores, index),
                box=_box_at(boxes, index),
            )
            for index, text in enumerate(txts)
        ]

    if isinstance(result, tuple) and result and isinstance(result[0], list):
        return [_legacy_line(item) for item in result[0] if item]

    return []


def _legacy_line(item: Any) -> _OcrLine:
    if len(item) < 3:
        return _OcrLine(text="", score=0.0, box=None)

    box, text, score = item[:3]
    return _OcrLine(text=str(text), score=_as_float(score), box=np.asarray(box, dtype=np.float32))


def _build_digit_sequence(line: _OcrLine) -> DigitSequence | None:
    text = _normalize_digits(line.text)
    if not text:
        return None

    left, top, width, height = _line_bounds(line.box)
    return DigitSequence(
        text=text,
        score=line.score,
        left=left,
        top=top,
        width=width,
        height=height,
    )


def _normalize_digits(text: str) -> str:
    if not _DIGIT_RE.search(text):
        return ""

    return _NON_DIGIT_RE.sub("", text)


def _line_bounds(box: np.ndarray | None) -> tuple[int, int, int, int]:
    if box is None or box.size == 0:
        return 0, 0, 0, 0

    points = np.asarray(box, dtype=np.float32).reshape(-1, 2)
    left = int(np.floor(points[:, 0].min()))
    top = int(np.floor(points[:, 1].min()))
    right = int(np.ceil(points[:, 0].max()))
    bottom = int(np.ceil(points[:, 1].max()))
    return left, top, max(0, right - left), max(0, bottom - top)


def _score_at(scores: Any, index: int) -> float:
    try:
        return _as_float(scores[index])
    except (IndexError, TypeError):
        return 0.0


def _box_at(boxes: Any, index: int) -> np.ndarray | None:
    if boxes is None:
        return None

    try:
        return np.asarray(boxes[index], dtype=np.float32)
    except (IndexError, TypeError):
        return None


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
