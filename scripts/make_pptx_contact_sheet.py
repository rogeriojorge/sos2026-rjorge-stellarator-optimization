#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a contact sheet from rendered slide PNG previews.")
    parser.add_argument("images", nargs="+", help="Preview PNGs in slide order.")
    parser.add_argument("--output", required=True, help="Output contact-sheet PNG.")
    parser.add_argument("--cols", type=int, default=5, help="Number of columns in the contact sheet.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    image_paths = [Path(value).expanduser().resolve() for value in args.images]
    missing = [path for path in image_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(missing[0])

    cols = max(1, args.cols)
    rows = math.ceil(len(image_paths) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.2, rows * 2.05), dpi=160)
    flat_axes = axes.ravel() if hasattr(axes, "ravel") else [axes]

    for ax, image_path in zip(flat_axes, image_paths):
        image = mpimg.imread(image_path)
        ax.imshow(image)
        ax.set_title(f"Slide {image_paths.index(image_path) + 1:02d}", fontsize=8, loc="left", pad=2)
        ax.axis("off")

    for ax in flat_axes[len(image_paths) :]:
        ax.axis("off")

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=0.25)
    fig.savefig(output, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
