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
        help="Kept for compatibility; RapidOCR does not use template variants. Default: auto.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="OCR confidence threshold. Higher values reduce false positives. Default: 0.80.",
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

    return recognize_digit_sequences(image, variant="small", threshold=threshold)


if __name__ == "__main__":
    main()
