#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
STATUS_DIR = ROOT / "data" / "generated" / "status"


def inline_config() -> Config:
    config = Config()
    config.InteractiveShellApp.matplotlib = "inline"
    config.InlineBackend.figure_format = "png"
    config.InlineBackend.rc = {"figure.dpi": 120}
    return config


def execute_one(path: Path) -> dict:
    try:
        notebook = nbformat.read(path, as_version=4)
        executor = ExecutePreprocessor(timeout=300, kernel_name="python3", config=inline_config())
        executor.preprocess(notebook, {"metadata": {"path": str(ROOT)}})
        nbformat.write(notebook, path)
        return {"name": path.name, "ok": True, "outputs": sum(len(cell.get("outputs", [])) for cell in notebook.cells if cell.cell_type == "code")}
    except Exception as exc:
        return {"name": path.name, "ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    results = [execute_one(path) for path in notebooks]
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "notebook_execution_in_place.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['name']}: {'OK' if item['ok'] else 'FAIL'}")
        if item.get("error"):
            print(f"  {item['error']}")
        else:
            print(f"  outputs: {item['outputs']}")
    return 0 if all(item["ok"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
