#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_MARKERS = [
    "/Users/" + "rogeriojorge",
    "/mnt/" + "data",
    "/private/" + "var",
    "/var/" + "folders",
    "C:" + "\\Users\\",
]
TEXT_SUFFIXES = {
    "",
    ".cff",
    ".cfg",
    ".css",
    ".html",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True)
    return [ROOT / line for line in output.splitlines() if line]


def main() -> int:
    problems: list[str] = []
    for path in tracked_files():
        rel = path.relative_to(ROOT)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in LOCAL_MARKERS:
            if marker in text:
                problems.append(f"{rel}: contains local path marker {marker!r}")
    if problems:
        print("Local-path audit failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Local-path audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
