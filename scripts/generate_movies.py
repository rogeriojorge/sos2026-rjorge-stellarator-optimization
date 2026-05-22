from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json
from sos2026.paths import STATUS_DIR, MOVIE_DIR, ensure_directories
from sos2026.movie_helpers import rotating_surface_gif, optimization_history_gif


def main() -> int:
    ensure_directories()
    results = []
    for label, func in [("rotating_surface", rotating_surface_gif), ("optimization_history", optimization_history_gif)]:
        try:
            path = func()
            results.append({"label": label, "ok": True, "path": str(path), "bytes": path.stat().st_size})
            print(f"{label}: OK -> {path}")
        except Exception as exc:
            results.append({"label": label, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            print(f"{label}: FAIL -> {exc}")
    movies = sorted(p.name for p in MOVIE_DIR.glob("*.gif"))
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "movies.json").write_text(json.dumps({"results": results, "movies": movies}, indent=2), encoding="utf-8")
    return 0 if sum(1 for r in results if r["ok"]) >= 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
