#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
STATUS_DIR = ROOT / "data" / "generated" / "status"


def audit_one(path: Path) -> dict:
    notebook = nbformat.read(path, as_version=4)
    counts: dict[str, int] = {}
    errors: list[dict[str, str | int]] = []
    rich_outputs = 0
    output_cells = 0

    for index, cell in enumerate(notebook.cells):
        outputs = cell.get("outputs", [])
        if outputs:
            output_cells += 1
        for output in outputs:
            output_type = output.get("output_type", "unknown")
            counts[output_type] = counts.get(output_type, 0) + 1
            if output_type == "error":
                errors.append(
                    {
                        "cell": index + 1,
                        "ename": output.get("ename", ""),
                        "evalue": output.get("evalue", ""),
                    }
                )
            data = output.get("data", {})
            if "image/png" in data or "application/vnd.plotly.v1+json" in data:
                rich_outputs += 1

    return {
        "name": path.name,
        "cell_count": len(notebook.cells),
        "output_cells": output_cells,
        "output_counts": counts,
        "rich_outputs": rich_outputs,
        "errors": errors,
        "ok": not errors and output_cells >= 5 and rich_outputs >= 2,
    }


def main() -> int:
    results = [audit_one(path) for path in sorted(NOTEBOOK_DIR.glob("*.ipynb"))]
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "notebook_output_audit.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    for item in results:
        print(
            f"{item['name']}: {'OK' if item['ok'] else 'FAIL'}; "
            f"cells={item['cell_count']}; output_cells={item['output_cells']}; "
            f"rich_outputs={item['rich_outputs']}; counts={item['output_counts']}"
        )
        for error in item["errors"]:
            print(f"  error in cell {error['cell']}: {error['ename']}: {error['evalue']}")

    return 0 if all(item["ok"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
