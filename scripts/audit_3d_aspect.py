#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEARCH_PATHS = [ROOT / "src", ROOT / "scripts", ROOT / "notebooks"]
ASPECT_HELPERS = ("fix_matplotlib_3d(", "frame_3d_axes(")


def source_blocks(path: Path) -> list[tuple[int, list[str]]]:
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        blocks = []
        offset = 1
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))
                lines = source.splitlines()
                blocks.append((offset, lines))
                offset += len(lines) + 3
        return blocks
    return [(1, path.read_text(encoding="utf-8").splitlines())]


def main() -> int:
    failures: list[str] = []
    checked = 0
    files = []
    for base in SEARCH_PATHS:
        files.extend(base.rglob("*.py"))
        files.extend(base.rglob("*.ipynb"))

    for path in sorted(set(files)):
        if ".ipynb_checkpoints" in path.parts:
            continue
        if path == Path(__file__).resolve():
            continue
        for base_line, lines in source_blocks(path):
            for index, line in enumerate(lines):
                if 'projection="3d"' not in line and "projection='3d'" not in line:
                    continue
                checked += 1
                window = "\n".join(lines[index : index + 24])
                if not any(helper in window for helper in ASPECT_HELPERS):
                    rel = path.relative_to(ROOT)
                    failures.append(f"{rel}:{base_line + index}: 3D axes without shared aspect/framing helper nearby")

    if failures:
        print("3D aspect audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"3D aspect audit passed for {checked} 3D axes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
