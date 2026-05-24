#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("smoke", [sys.executable, "scripts/run_smoke_tests.py"]),
    ("fetch minimal data", [sys.executable, "scripts/fetch_equilibria.py", "--minimal"]),
    ("generate figures", [sys.executable, "scripts/generate_all_figures.py"]),
    ("generate movies", [sys.executable, "scripts/generate_movies.py"]),
    ("execute core notebooks", [sys.executable, "scripts/execute_notebooks_core.py"]),
    ("execute all notebooks", [sys.executable, "scripts/execute_all_notebooks.py"]),
    ("execute notebooks in place", [sys.executable, "scripts/execute_notebooks_in_place.py"]),
    ("regenerate final figures", [sys.executable, "scripts/generate_all_figures.py"]),
    ("regenerate final movies", [sys.executable, "scripts/generate_movies.py"]),
    ("audit no local paths", [sys.executable, "scripts/audit_no_local_paths.py"]),
    ("audit ReadTheDocs links", [sys.executable, "scripts/audit_readthedocs_links.py"]),
    ("audit figure whitespace", [sys.executable, "scripts/audit_figure_whitespace.py"]),
    ("audit 3D aspect", [sys.executable, "scripts/audit_3d_aspect.py"]),
    ("audit notebook outputs", [sys.executable, "scripts/audit_notebook_outputs.py"]),
    ("audit slide style", [sys.executable, "scripts/audit_slides_style.py"]),
    ("status report", [sys.executable, "scripts/make_status_report.py"]),
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
]


def run_step(label: str, command: list[str]) -> dict:
    started = time.time()
    print(f"\n== {label} ==", flush=True)
    print(" ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True)
    elapsed = time.time() - started
    return {
        "label": label,
        "command": " ".join(command),
        "returncode": completed.returncode,
        "elapsed_seconds": round(elapsed, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the cached-mode release-readiness checks.")
    parser.add_argument(
        "--skip-status-report",
        action="store_true",
        help="Skip make_status_report.py. CI runs it in an always() step so failures still get a report.",
    )
    args = parser.parse_args(argv)

    selected = [
        (label, command)
        for label, command in COMMANDS
        if not (args.skip_status_report and label == "status report")
    ]
    results = [run_step(label, command) for label, command in selected]

    print("\n== summary ==", flush=True)
    for result in results:
        status = "OK" if result["returncode"] == 0 else "FAIL"
        print(f"{status:4} {result['label']:<24} {result['elapsed_seconds']:>6.1f}s")

    failures = [result for result in results if result["returncode"] != 0]
    if failures:
        print("\nRelease-readiness check failed.")
        return 1
    print("\nRelease-readiness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
