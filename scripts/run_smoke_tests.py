from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import importlib
import json
import platform

from sos2026.paths import PROJECT_ROOT, STATUS_DIR, ensure_directories, CACHE_DIR, FIGURE_DIR, NOTEBOOK_DIR

CORE = ["numpy", "scipy", "matplotlib", "pandas", "xarray", "netCDF4", "h5py", "nbformat", "nbconvert", "pytest"]
OPTIONAL = {
    "jax": "jax",
    "vmec_jax": "vmec_jax",
    "booz_xform_jax": "booz_xform_jax",
    "NEO_JAX": "neo_jax",
    "sfincs_jax": "sfincs_jax",
    "SPECTRAX-GK": "spectrax",
    "SIMSOPT": "simsopt",
    "NEOPAX": "NEOPAX",
    "ESSOS": "essos",
}
REQUIRED_NOTEBOOKS = [
    "00_environment_check.ipynb", "01_vmec_jax_first_equilibrium.ipynb", "02_boozer_spectrum.ipynb",
    "03_effective_ripple_neo_jax.ipynb", "04_simsopt_stage2_coils.ipynb", "05_single_stage_toy.ipynb",
    "06_essos_fieldlines_particles.ipynb", "07_sfincs_jax_neoclassical_cached.ipynb", "08_spectrax_gk_linear_metric.ipynb",
    "09_turbulence_metric_surrogate.ipynb", "10_neopax_profile_closure.ipynb", "11_pareto_design_dashboard.ipynb",
]


def import_status(name: str) -> dict:
    try:
        mod = importlib.import_module(name)
        return {"ok": True, "version": getattr(mod, "__version__", "unknown"), "file": str(getattr(mod, "__file__", "namespace"))}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def notebook_has_run_mode(path: Path) -> bool:
    try:
        import nbformat
        nb = nbformat.read(path, as_version=4)
        return any("RUN_MODE" in (cell.get("source") or "") for cell in nb.cells)
    except Exception:
        return False


def main() -> int:
    ensure_directories()
    core = {name: import_status(name) for name in CORE}
    optional = {label: import_status(module) for label, module in OPTIONAL.items()}
    folders = {str(p.relative_to(PROJECT_ROOT)): p.exists() for p in [CACHE_DIR, FIGURE_DIR, NOTEBOOK_DIR]}
    notebooks = {name: {"exists": (NOTEBOOK_DIR / name).exists(), "has_RUN_MODE": notebook_has_run_mode(NOTEBOOK_DIR / name)} for name in REQUIRED_NOTEBOOKS}
    data = {
        "HSX wout": (PROJECT_ROOT / "data/vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc").exists(),
        "W7-X wout": (PROJECT_ROOT / "data/vmec_equilibria/W7-X/Standard/wout.nc").exists(),
        "cached files": len(list(CACHE_DIR.glob("*"))),
    }
    report = {"python": platform.python_version(), "core": core, "optional": optional, "folders": folders, "notebooks": notebooks, "data": data}
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "smoke_tests.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Python: {platform.python_version()}")
    print("Core packages:", "OK" if all(item["ok"] for item in core.values()) else "CHECK")
    print("Optional scientific packages:")
    for label, status in optional.items():
        print(f"  {label}: {'OK' if status['ok'] else 'missing/fail'}")
    print("Data:")
    for label, status in data.items():
        print(f"  {label}: {status}")
    print("Notebooks:")
    for name, status in notebooks.items():
        state = "OK" if status["exists"] and status["has_RUN_MODE"] else "CHECK"
        print(f"  {name}: {state}")
    return 0 if all(item["ok"] for item in core.values()) and all(v["exists"] and v["has_RUN_MODE"] for v in notebooks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
