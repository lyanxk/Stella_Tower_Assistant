from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal

import cv2

if __package__ in (None, ""):
    SRC_DIR = Path(__file__).resolve().parents[1]
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    from stellatowerassistant.core.automation.ocr import recognize_digit_sequences
else:
    from .core.automation.ocr import recognize_digit_sequences

OcrVariant = Literal["auto", "small", "elevator"]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m stellatowerassistant.ocr_image_cli",
        description="Recognize digit sequences from one or more local images and print them to the console.",
    )
    parser.add_argument("images", nargs="+", help="Path to image file(s) to recognize.")
    parser.add_argument(
        "--variant",
        choices=("auto", "small", "elevator"),
        default="auto",
        help="Digit template set to use. Default: auto.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.92,
        help="Template match threshold. Higher values reduce false positives. Default: 0.92.",
    )
    args = parser.parse_args()

    image_paths = [Path(item).expanduser().resolve() for item in args.images]
    for path in image_paths:
        sequences = recognize_sequences_from_image_path(path, variant=args.variant, threshold=args.threshold)
        output = ",".join(sequences)
        if len(image_paths) == 1:
            print(output, flush=True)
        else:
            print(f"{path}: {output}", flush=True)


def recognize_sequences_from_image_path(
    image_path: Path,
    variant: OcrVariant,
    threshold: float,
) -> list[str]:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError(f"Unable to read image: {image_path}")

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
