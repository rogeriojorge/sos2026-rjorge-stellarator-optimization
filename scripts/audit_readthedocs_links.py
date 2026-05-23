#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_URL = "https://sos2026-rjorge-stellarator-optimization.readthedocs.io/"
REQUIRED = [
    "README.md",
    "docs/index.md",
    "docs/install.md",
    "docs/instructor_checklist.md",
    "docs/live_demo_matrix.md",
    "docs/teaching_notes.md",
    "slides/lecture_4_integrated_workflow.md",
    "slides/powerpoint/deck_spec.json",
]
OPTIONAL_IF_PRESENT = [
    "dist/sos2026_lecture_bundle/README_FOR_INSTRUCTOR.md",
]


def main() -> int:
    problems: list[str] = []
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        if DOCS_URL not in path.read_text(encoding="utf-8"):
            problems.append(f"{rel}: missing ReadTheDocs URL")
    for rel in OPTIONAL_IF_PRESENT:
        path = ROOT / rel
        if path.exists() and DOCS_URL not in path.read_text(encoding="utf-8"):
            problems.append(f"{rel}: missing ReadTheDocs URL")
    if problems:
        print("ReadTheDocs link audit failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("ReadTheDocs link audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
