from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

from sos2026.paths import NOTEBOOK_DIR, GENERATED_DIR, STATUS_DIR, PROJECT_ROOT, ensure_directories

CORE_NOTEBOOKS = [
    "00_environment_check.ipynb",
    "01_vmec_jax_first_equilibrium.ipynb",
    "02_boozer_spectrum.ipynb",
    "03_effective_ripple_neo_jax.ipynb",
    "04_simsopt_stage2_coils.ipynb",
    "09_turbulence_metric_surrogate.ipynb",
    "11_pareto_design_dashboard.ipynb",
]


def inline_config() -> Config:
    config = Config()
    config.InteractiveShellApp.matplotlib = "inline"
    config.InlineBackend.figure_format = "png"
    config.InlineBackend.rc = {"figure.dpi": 120}
    return config


def execute_one(name: str) -> dict:
    in_path = NOTEBOOK_DIR / name
    out_dir = GENERATED_DIR / "notebook_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / name
    try:
        nb = nbformat.read(in_path, as_version=4)
        ep = ExecutePreprocessor(timeout=180, kernel_name="python3", config=inline_config())
        ep.preprocess(nb, {"metadata": {"path": str(PROJECT_ROOT)}})
        nbformat.write(nb, out_path)
        return {"name": name, "ok": True, "executed_copy": str(out_path.relative_to(PROJECT_ROOT))}
    except Exception as exc:
        return {"name": name, "ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    ensure_directories()
    results = [execute_one(name) for name in CORE_NOTEBOOKS]
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "notebook_execution.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['name']}: {'OK' if item['ok'] else 'FAIL'}")
        if not item["ok"]:
            print(f"  {item['error']}")
    return 0 if all(item["ok"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
