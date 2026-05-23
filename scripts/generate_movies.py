from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import hashlib
import json
from sos2026.paths import STATUS_DIR, MOVIE_DIR, ensure_directories
from sos2026.movie_helpers import rotating_surface_gif, optimization_history_gif


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    ensure_directories()
    results = []
    for label, func in [("rotating_surface", rotating_surface_gif), ("optimization_history", optimization_history_gif)]:
        try:
            path = func()
            first_frame = path.with_name(f"{path.stem}_first_frame.png")
            results.append({
                "label": label,
                "ok": True,
                "path": str(path),
                "bytes": path.stat().st_size,
                "first_frame": str(first_frame),
                "first_frame_bytes": first_frame.stat().st_size if first_frame.exists() else 0,
                "category": "synthetic educational fallback",
                "sha256": sha256(path),
                "caption": "Small classroom GIF generated from cached/synthetic teaching geometry.",
                "regenerate": "python scripts/generate_movies.py",
            })
            print(f"{label}: OK -> {path}")
        except Exception as exc:
            results.append({"label": label, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            print(f"{label}: FAIL -> {exc}")
    movies = sorted(p.name for p in MOVIE_DIR.glob("*.gif"))
    first_frames = sorted(p.name for p in MOVIE_DIR.glob("*_first_frame.png"))
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "movies.json").write_text(json.dumps({"results": results, "movies": movies, "first_frames": first_frames}, indent=2), encoding="utf-8")
    return 0 if sum(1 for r in results if r["ok"]) >= 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
