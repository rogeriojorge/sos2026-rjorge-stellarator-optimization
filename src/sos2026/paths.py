from __future__ import annotations

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    start = Path(start or __file__).resolve()
    candidates = [start] + list(start.parents)
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "sos2026").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
VMEC_DIR = DATA_DIR / "vmec_equilibria"
INPUT_DIR = DATA_DIR / "inputs"
CACHE_DIR = DATA_DIR / "cached"
GENERATED_DIR = DATA_DIR / "generated"
FIGURE_DIR = PROJECT_ROOT / "assets" / "figures"
MOVIE_DIR = PROJECT_ROOT / "assets" / "movies"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
STATUS_DIR = GENERATED_DIR / "status"


def ensure_directories() -> None:
    for path in [DATA_DIR, VMEC_DIR, INPUT_DIR, CACHE_DIR, GENERATED_DIR, FIGURE_DIR, MOVIE_DIR, NOTEBOOK_DIR, STATUS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
