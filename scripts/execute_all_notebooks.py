#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
GENERATED_DIR = ROOT / "data" / "generated"
STATUS_DIR = GENERATED_DIR / "status"


def execute_one(path: Path) -> dict:
    out_dir = GENERATED_DIR / "notebook_runs_all"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / path.name
    try:
        nb = nbformat.read(path, as_version=4)
        ep = ExecutePreprocessor(timeout=240, kernel_name="python3")
        ep.preprocess(nb, {"metadata": {"path": str(ROOT)}})
        nbformat.write(nb, out_path)
        return {"name": path.name, "ok": True, "executed_copy": str(out_path.relative_to(ROOT))}
    except Exception as exc:
        return {"name": path.name, "ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    results = [execute_one(path) for path in notebooks]
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "notebook_execution_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['name']}: {'OK' if item['ok'] else 'FAIL'}")
        if item.get("error"):
            print(f"  {item['error']}")
    return 0 if all(item["ok"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
