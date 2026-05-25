#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "slides/powerpoint/deck_spec.json"
DOCS_URL = "https://sos2026-rjorge-stellarator-optimization.readthedocs.io/"
PLACEHOLDERS = [
    "Optimization question",
    "Code or data object",
    "Plot to read",
    "Failure mode to remember",
    "Extra slide",
    "What would you trust",
]
DECK_IDS = [
    "lecture_1_geometry_metrics",
    "lecture_2_coils_single_stage",
    "lecture_3_transport_turbulence_metrics",
    "lecture_4_integrated_workflow",
]


def slide_text(slide: dict) -> str:
    values: list[str] = []
    for value in slide.values():
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            values.extend(str(item) for item in value)
    return "\n".join(values)


def main() -> int:
    problems: list[str] = []
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    decks = {deck["id"]: deck for deck in spec.get("decks", [])}
    for deck_id in DECK_IDS:
        if deck_id not in decks:
            problems.append(f"{deck_id}: missing from deck spec")
            continue
        deck = decks[deck_id]
        slides = deck.get("slides", [])
        if not 30 <= len(slides) <= 50:
            problems.append(f"{deck_id}: expected 30-50 slides, found {len(slides)}")

        pptx = ROOT / "slides" / "pptx" / f"{deck_id}.pptx"
        contact = ROOT / "slides" / "pptx" / "contact_sheets" / f"{deck_id}_contact_sheet.png"
        if not pptx.exists():
            problems.append(f"{deck_id}: missing PPTX")
        if not contact.exists():
            problems.append(f"{deck_id}: missing contact sheet")

        joined = "\n".join(slide_text(slide) for slide in slides)
        for phrase in PLACEHOLDERS:
            if phrase.lower() in joined.lower():
                problems.append(f"{deck_id}: placeholder phrase remains: {phrase!r}")
        if not any(str(slide.get("title", "")).startswith("PART ") for slide in slides):
            problems.append(f"{deck_id}: no PART divider")

        appendix_index = next((i for i, slide in enumerate(slides) if str(slide.get("title", "")).upper().startswith("APPENDIX")), min(30, len(slides)))
        core = slides[:appendix_index]
        visual_core = [
            slide for slide in core
            if slide.get("image")
            or slide.get("kind")
            in {"workflow", "diagram", "project", "demo", "movie", "title", "transition", "quote", "table", "code_table", "ladder", "warning", "code", "explainer"}
        ]
        if core and len(visual_core) / len(core) < 0.65:
            problems.append(f"{deck_id}: too few core slides have a visual/proof object ({len(visual_core)}/{len(core)})")

        figure_refs = [slide.get("image") for slide in slides if str(slide.get("image", "")).startswith("assets/figures/")]
        missing_figs = [ref for ref in figure_refs if not (ROOT / ref).exists()]
        if missing_figs:
            problems.append(f"{deck_id}: missing referenced figures {missing_figs[:3]}")

    lecture4 = decks.get("lecture_4_integrated_workflow", {})
    if DOCS_URL not in "\n".join(slide_text(slide) for slide in lecture4.get("slides", [])):
        problems.append("lecture_4_integrated_workflow: missing ReadTheDocs URL")

    if problems:
        print("Slide style audit failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Slide style audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
