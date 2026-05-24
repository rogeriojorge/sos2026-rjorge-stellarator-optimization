#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "assets" / "figures"

MAX_GENERAL_WHITESPACE = 0.38
MAX_THIN_3D_WHITESPACE = 0.56
THIN_3D_FIGURES = {
    "04_initial_coils.png",
    "04_final_coils.png",
    "06_fieldlines.png",
}


def whitespace_fraction(path: Path, threshold: int = 12) -> tuple[float, tuple[int, int, int, int]]:
    image = Image.open(path).convert("RGB")
    white = Image.new("RGB", image.size, "white")
    diff = ImageChops.difference(image, white).convert("L")
    bbox = diff.point(lambda value: 255 if value > threshold else 0).getbbox()
    if bbox is None:
        return 1.0, (0, 0, image.size[0], image.size[1])
    left, top, right, bottom = bbox
    content_area = (right - left) * (bottom - top)
    return 1.0 - content_area / (image.size[0] * image.size[1]), (
        left,
        top,
        image.size[0] - right,
        image.size[1] - bottom,
    )


def main() -> int:
    failures: list[str] = []
    rows = []
    for path in sorted(FIGURE_DIR.glob("*.png")):
        fraction, margins = whitespace_fraction(path)
        limit = MAX_THIN_3D_WHITESPACE if path.name in THIN_3D_FIGURES else MAX_GENERAL_WHITESPACE
        rows.append((fraction, path.name, margins, limit))
        if fraction > limit:
            failures.append(f"{path.name}: {fraction:.1%} whitespace exceeds {limit:.1%}; margins={margins}")

    for fraction, name, margins, limit in sorted(rows, reverse=True):
        marker = "FAIL" if fraction > limit else "OK"
        print(f"{marker:4s} {fraction:5.1%} {name:38s} margins={margins}")

    if failures:
        print("\nWhitespace audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nFigure whitespace audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
