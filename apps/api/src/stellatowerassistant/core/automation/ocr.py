from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import cv2
import numpy as np

from ..config.settings import RESOURCE_DIR
from .vision import match_template_scores

DigitTemplateVariant = Literal["small", "elevator"]

DEFAULT_DIGIT_MATCH_THRESHOLD = 0.92
DEFAULT_DIGIT_MAX_GAP_RATIO = 1.5
DEFAULT_ROW_ALIGNMENT_RATIO = 0.6

_DIGIT_TEMPLATE_SUFFIXES: dict[DigitTemplateVariant, str] = {
    "small": "_s",
    "elevator": "_e",
}


@dataclass(frozen=True)
class DigitTemplate:
    digit: str
    image: np.ndarray

    @property
    def width(self) -> int:
        return int(self.image.shape[1])

    @property
    def height(self) -> int:
        return int(self.image.shape[0])


@dataclass(frozen=True)
class DigitCandidate:
    digit: str
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

    @property
    def center_x(self) -> float:
        return self.left + self.width / 2

    @property
    def center_y(self) -> float:
        return self.top + self.height / 2


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


@dataclass
class _DigitRow:
    candidates: list[DigitCandidate]
    center_y: float
    average_height: float

    def add(self, candidate: DigitCandidate) -> None:
        self.candidates.append(candidate)
        count = len(self.candidates)
        self.center_y = ((self.center_y * (count - 1)) + candidate.center_y) / count
        self.average_height = ((self.average_height * (count - 1)) + candidate.height) / count


@lru_cache(maxsize=None)
def load_digit_templates(variant: DigitTemplateVariant = "small") -> tuple[DigitTemplate, ...]:
    suffix = _DIGIT_TEMPLATE_SUFFIXES.get(variant)
    if suffix is None:
        raise ValueError(f"Unsupported digit template variant: {variant}")

    templates: list[DigitTemplate] = []
    for digit in "0123456789":
        path = RESOURCE_DIR / f"{digit}{suffix}.png"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None or image.size == 0:
            continue
        templates.append(DigitTemplate(digit=digit, image=image))

    if not templates:
        raise ValueError(f"No digit templates found for variant: {variant}")

    return tuple(templates)


def recognize_digit_sequences(
    source: np.ndarray,
    variant: DigitTemplateVariant = "small",
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
    variant: DigitTemplateVariant = "small",
    threshold: float = DEFAULT_DIGIT_MATCH_THRESHOLD,
    max_gap_ratio: float = DEFAULT_DIGIT_MAX_GAP_RATIO,
    row_alignment_ratio: float = DEFAULT_ROW_ALIGNMENT_RATIO,
) -> list[DigitSequence]:
    candidates = find_digit_candidates(source, variant=variant, threshold=threshold)
    if not candidates:
        return []

    sequences: list[DigitSequence] = []
    for row in _group_candidates_by_row(candidates, row_alignment_ratio=row_alignment_ratio):
        for group in _split_row_by_gap(row, max_gap_ratio=max_gap_ratio):
            sequences.append(_build_sequence(group))

    return sequences


def find_digit_candidates(
    source: np.ndarray,
    variant: DigitTemplateVariant = "small",
    threshold: float = DEFAULT_DIGIT_MATCH_THRESHOLD,
) -> list[DigitCandidate]:
    if source is None:
        return []

    candidates: list[DigitCandidate] = []
    for template in load_digit_templates(variant):
        scores = match_template_scores(source, template.image)
        if scores.size == 0:
            continue

        ys, xs = np.where(scores >= threshold)
        for y, x in zip(ys.tolist(), xs.tolist()):
            candidates.append(
                DigitCandidate(
                    digit=template.digit,
                    score=float(scores[y, x]),
                    left=int(x),
                    top=int(y),
                    width=template.width,
                    height=template.height,
                )
            )

    return _deduplicate_candidates(candidates)


def _deduplicate_candidates(candidates: list[DigitCandidate]) -> list[DigitCandidate]:
    kept: list[DigitCandidate] = []
    for candidate in sorted(candidates, key=lambda item: (-item.score, item.top, item.left)):
        if any(_is_same_detection(candidate, existing) for existing in kept):
            continue
        kept.append(candidate)

    kept.sort(key=lambda item: (item.center_y, item.left))
    return kept


def _build_sequence(candidates: list[DigitCandidate]) -> DigitSequence:
    left = min(candidate.left for candidate in candidates)
    top = min(candidate.top for candidate in candidates)
    right = max(candidate.right for candidate in candidates)
    bottom = max(candidate.bottom for candidate in candidates)
    score = sum(candidate.score for candidate in candidates) / len(candidates)
    return DigitSequence(
        text="".join(candidate.digit for candidate in candidates),
        score=score,
        left=left,
        top=top,
        width=right - left,
        height=bottom - top,
    )


def _is_same_detection(left: DigitCandidate, right: DigitCandidate) -> bool:
    horizontal_overlap = min(left.right, right.right) - max(left.left, right.left)
    vertical_overlap = min(left.bottom, right.bottom) - max(left.top, right.top)
    if horizontal_overlap > 0 and vertical_overlap > 0:
        return True

    max_center_dx = min(left.width, right.width) * 0.5
    max_center_dy = min(left.height, right.height) * 0.5
    return abs(left.center_x - right.center_x) <= max_center_dx and abs(left.center_y - right.center_y) <= max_center_dy


def _group_candidates_by_row(
    candidates: list[DigitCandidate],
    row_alignment_ratio: float,
) -> list[list[DigitCandidate]]:
    rows: list[_DigitRow] = []
    for candidate in sorted(candidates, key=lambda item: (item.center_y, item.left)):
        matching_row = _find_matching_row(rows, candidate, row_alignment_ratio=row_alignment_ratio)
        if matching_row is None:
            rows.append(
                _DigitRow(
                    candidates=[candidate],
                    center_y=candidate.center_y,
                    average_height=float(candidate.height),
                )
            )
            continue
        matching_row.add(candidate)

    rows.sort(key=lambda row: row.center_y)
    return [sorted(row.candidates, key=lambda item: item.left) for row in rows]


def _find_matching_row(
    rows: list[_DigitRow],
    candidate: DigitCandidate,
    row_alignment_ratio: float,
) -> _DigitRow | None:
    for row in rows:
        tolerance = max(row.average_height, candidate.height) * row_alignment_ratio
        if abs(candidate.center_y - row.center_y) <= tolerance:
            return row
    return None


def _split_row_by_gap(candidates: list[DigitCandidate], max_gap_ratio: float) -> list[list[DigitCandidate]]:
    if not candidates:
        return []

    groups: list[list[DigitCandidate]] = [[candidates[0]]]
    for candidate in candidates[1:]:
        previous = groups[-1][-1]
        gap = candidate.left - previous.right
        max_gap = max(previous.width, candidate.width) * max_gap_ratio
        if gap > max_gap:
            groups.append([candidate])
            continue
        groups[-1].append(candidate)

    return groups
