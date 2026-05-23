#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/generated/status/powerpoint_decks.json"
SPEC = ROOT / "slides/powerpoint/deck_spec.json"
SLIDE_W = 1280
SLIDE_H = 720

FORBIDDEN_PHRASES = [
    "Extra slide",
    "What would you trust in cached mode?",
    "it's not",
    "it is not this",
    "not this,",
    "not that",
]


def composite_on_white(image: np.ndarray) -> np.ndarray:
    if image.ndim != 3:
        return image
    rgb = image[..., :3].astype(float)
    if rgb.max() > 1:
        rgb /= 255.0
    if image.shape[2] < 4:
        return rgb
    alpha = image[..., 3:4].astype(float)
    if alpha.max() > 1:
        alpha /= 255.0
    return rgb * alpha + np.ones_like(rgb) * (1.0 - alpha)


def read_texts(layout_path: Path) -> list[str]:
    layout = json.loads(layout_path.read_text())
    texts: list[str] = []
    for element in layout.get("elements", []):
        value = element.get("text")
        if isinstance(value, str) and value.strip():
            texts.append(value.strip())
    return texts


def has_uw_red_mark(image: np.ndarray) -> bool:
    height, width = image.shape[:2]
    crop = image[: int(0.16 * height), int(0.91 * width) :]
    if crop.size == 0:
        return False
    red = (crop[..., 0] > 0.55) & (crop[..., 1] < 0.18) & (crop[..., 2] < 0.18)
    return int(red.sum()) > max(100, int(0.001 * crop.shape[0] * crop.shape[1]))


def assert_no_forbidden_text(deck_id: str, slide_number: int, texts: list[str]) -> list[str]:
    problems: list[str] = []
    joined = "\n".join(texts)
    lowered = joined.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lowered:
            problems.append(f"{deck_id} slide {slide_number:02d}: forbidden phrase {phrase!r}")
    return problems


def main() -> int:
    if not MANIFEST.exists():
        print(f"Missing {MANIFEST.relative_to(ROOT)}. Run scripts/build_powerpoint_decks.mjs first.", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text())
    spec = json.loads(SPEC.read_text())
    deck_specs = {deck["id"]: deck for deck in spec["decks"]}

    problems: list[str] = []
    checked = 0
    for deck in manifest.get("decks", []):
        deck_id = deck["id"]
        expected = deck_specs.get(deck_id)
        if expected is None:
            problems.append(f"{deck_id}: no matching deck spec")
            continue

        output = Path(deck["output"])
        contact_sheet = Path(deck["contactSheet"])
        preview_dir = Path(deck["previewDir"])
        layout_dir = Path(deck["layoutDir"])
        for path in [output, contact_sheet, preview_dir, layout_dir]:
            if not path.exists():
                problems.append(f"{deck_id}: missing {path}")

        previews = sorted(preview_dir.glob("slide-*.png"))
        layouts = sorted(layout_dir.glob("slide-*.layout.json"))
        slide_count = int(deck["slideCount"])
        if slide_count != len(expected["slides"]):
            problems.append(f"{deck_id}: manifest has {slide_count} slides, spec has {len(expected['slides'])}")
        if len(previews) != slide_count:
            problems.append(f"{deck_id}: expected {slide_count} previews, found {len(previews)}")
        if len(layouts) != slide_count:
            problems.append(f"{deck_id}: expected {slide_count} layouts, found {len(layouts)}")

        for index, item in enumerate(expected["slides"], start=1):
            checked += 1
            preview_path = preview_dir / f"slide-{index:02d}.png"
            layout_path = layout_dir / f"slide-{index:02d}.layout.json"
            if not preview_path.exists() or not layout_path.exists():
                problems.append(f"{deck_id} slide {index:02d}: missing preview or layout")
                continue

            image = composite_on_white(mpimg.imread(preview_path))
            if image.ndim != 3:
                problems.append(f"{deck_id} slide {index:02d}: preview is not RGB/RGBA")
                continue
            if image.shape[0] < 200 or image.shape[1] < 300:
                problems.append(f"{deck_id} slide {index:02d}: preview too small {image.shape[:2]}")
            if float(image[..., :3].std()) < 0.015:
                problems.append(f"{deck_id} slide {index:02d}: preview appears blank")
            if not has_uw_red_mark(image):
                problems.append(f"{deck_id} slide {index:02d}: UW red mark not detected in preview")

            texts = read_texts(layout_path)
            expected_title = str(item.get("title", "")).strip()
            if expected_title and not any(expected_title in text for text in texts):
                problems.append(f"{deck_id} slide {index:02d}: title missing from exported layout")
            slide_number = f"Slide {index:02d}"
            if not any(slide_number in text for text in texts):
                problems.append(f"{deck_id} slide {index:02d}: slide number missing from exported layout")
            problems.extend(assert_no_forbidden_text(deck_id, index, texts))

    if problems:
        print("PowerPoint preview audit failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(f"PowerPoint preview audit passed for {checked} slides across {len(manifest.get('decks', []))} decks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
