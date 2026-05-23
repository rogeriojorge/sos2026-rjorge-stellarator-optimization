#!/usr/bin/env python3
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_URL = "https://sos2026-rjorge-stellarator-optimization.readthedocs.io/"
BUNDLE_ROOT = ROOT / "dist" / "sos2026_lecture_bundle"
ZIP_PATH = ROOT / "dist" / "sos2026_rjorge_lecture_bundle.zip"


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_tree(src: Path, dest: Path, patterns: tuple[str, ...]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for path in sorted(src.glob(pattern)):
            if path.is_file() and ".ipynb_checkpoints" not in path.parts:
                copy_file(path, dest / path.name)


def write_instructor_readme() -> None:
    text = f"""# SOS 2026 Lecture Bundle

This bundle is a portable copy of the teaching artifacts for Rogerio Jorge's SOS 2026 stellarator optimization lectures.

Canonical rendered documentation: {DOCS_URL}

## Classroom default

Use cached mode first. The notebooks are committed with outputs so students can inspect plots on GitHub or run the same cached path locally.

## Contents

- `slides/pptx/`: editable PowerPoint decks.
- `slides/contact_sheets/`: thumbnail review sheets for the decks.
- `notebooks/`: Jupyter notebooks with cached-mode outputs.
- `assets/figures/`: generated teaching figures and `manifest.json`.
- `assets/movies/`: small GIFs plus first-frame PNGs for PowerPoint compatibility.
- `docs/`: documentation source; the live rendered version is on ReadTheDocs.
- `data/`: cached classroom data plus minimal public inputs.
- `scripts/` and `src/`: regeneration and audit code.
- `STATUS.md`: current package, data, notebook, figure, movie, and deck status.

## Day-before command sequence

```bash
python -m pip install -r requirements-core.txt -e .
python scripts/check_release_ready.py
python scripts/audit_notebook_outputs.py
```

Keep a cached fallback slide ready for every live demo. The cached figures teach how to read the metric; they are not new validated physics calculations.
"""
    (BUNDLE_ROOT / "README_FOR_INSTRUCTOR.md").write_text(text, encoding="utf-8")


def make_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(BUNDLE_ROOT.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(BUNDLE_ROOT.parent))


def main() -> int:
    if BUNDLE_ROOT.exists():
        shutil.rmtree(BUNDLE_ROOT)
    BUNDLE_ROOT.mkdir(parents=True, exist_ok=True)

    copy_file(ROOT / "README.md", BUNDLE_ROOT / "README.md")
    copy_file(ROOT / "STATUS.md", BUNDLE_ROOT / "STATUS.md")
    copy_file(ROOT / "requirements-core.txt", BUNDLE_ROOT / "requirements-core.txt")
    copy_file(ROOT / "requirements-colab.txt", BUNDLE_ROOT / "requirements-colab.txt")
    copy_file(ROOT / "pyproject.toml", BUNDLE_ROOT / "pyproject.toml")

    copy_tree(ROOT / "slides" / "pptx", BUNDLE_ROOT / "slides" / "pptx", ("*.pptx",))
    copy_tree(ROOT / "slides" / "pptx" / "contact_sheets", BUNDLE_ROOT / "slides" / "contact_sheets", ("*.png",))
    copy_tree(ROOT / "notebooks", BUNDLE_ROOT / "notebooks", ("*.ipynb",))
    copy_tree(ROOT / "assets" / "figures", BUNDLE_ROOT / "assets" / "figures", ("*.png", "*.json"))
    copy_tree(ROOT / "assets" / "movies", BUNDLE_ROOT / "assets" / "movies", ("*.gif", "*.png"))
    copy_tree(ROOT / "docs", BUNDLE_ROOT / "docs", ("*.md", "*.py"))
    copy_tree(ROOT / "data" / "cached", BUNDLE_ROOT / "data" / "cached", ("*",))
    copy_tree(ROOT / "data" / "inputs" / "simsopt", BUNDLE_ROOT / "data" / "inputs" / "simsopt", ("*",))
    copy_tree(ROOT / "data" / "vmec_equilibria" / "HSX" / "QHS_vac_ns201_fixed", BUNDLE_ROOT / "data" / "vmec_equilibria" / "HSX" / "QHS_vac_ns201_fixed", ("*.nc",))
    copy_tree(ROOT / "data" / "vmec_equilibria" / "W7-X" / "Standard", BUNDLE_ROOT / "data" / "vmec_equilibria" / "W7-X" / "Standard", ("*.nc",))
    copy_tree(ROOT / "scripts", BUNDLE_ROOT / "scripts", ("*.py", "*.mjs"))
    copy_tree(ROOT / "src" / "sos2026", BUNDLE_ROOT / "src" / "sos2026", ("*.py",))

    write_instructor_readme()
    make_zip()
    print(f"Created {BUNDLE_ROOT.relative_to(ROOT)}")
    print(f"Created {ZIP_PATH.relative_to(ROOT)} ({ZIP_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
