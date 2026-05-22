from __future__ import annotations

from pathlib import Path
import numpy as np


def synthetic_surface(case: str = "hsx", ntheta: int = 64, nphi: int = 96) -> dict:
    theta = np.linspace(0, 2 * np.pi, ntheta)
    phi = np.linspace(0, 2 * np.pi, nphi)
    tt, pp = np.meshgrid(theta, phi, indexing="ij")
    if case.lower().startswith("w7"):
        nfp, helical, elong, triangular = 5, 0.055, 0.20, 0.025
        r0, a = 1.15, 0.22
    else:
        nfp, helical, elong, triangular = 4, 0.075, 0.11, 0.035
        r0, a = 1.0, 0.20
    r = r0 + a * np.cos(tt) + helical * np.cos(tt - nfp * pp) + triangular * np.cos(2 * tt + nfp * pp)
    z = a * (1 + elong * np.cos(nfp * pp)) * np.sin(tt) + 0.45 * helical * np.sin(tt + nfp * pp)
    x = r * np.cos(pp)
    y = r * np.sin(pp)
    return {"theta": theta, "phi": phi, "x": x, "y": y, "z": z, "case": case, "source": "synthetic educational surface"}


def find_primary_wout(project_root: Path, case: str = "hsx") -> Path | None:
    if case.lower().startswith("w7"):
        rel = Path("data/vmec_equilibria/W7-X/Standard/wout.nc")
    else:
        rel = Path("data/vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc")
    path = project_root / rel
    return path if path.exists() else None


def load_iota_profile(wout_path: Path | None = None, n: int = 64):
    if wout_path and Path(wout_path).exists():
        try:
            import xarray as xr
            with xr.open_dataset(wout_path) as ds:
                for name in ["iotaf", "iotas", "iota"]:
                    if name in ds:
                        arr = np.asarray(ds[name].values, dtype=float).ravel()
                        arr = arr[np.isfinite(arr)]
                        if arr.size > 4:
                            s = np.linspace(0, 1, arr.size)
                            return s, arr, f"read from {Path(wout_path).name}:{name}"
        except Exception as exc:
            return synthetic_iota(n=n)[:2] + (f"synthetic fallback after read failure: {exc}",)
    return synthetic_iota(n=n)


def synthetic_iota(n: int = 64):
    s = np.linspace(0, 1, n)
    iota = 0.82 + 0.24 * s - 0.035 * np.cos(2 * np.pi * s)
    return s, iota, "synthetic educational iota profile"


def boundary_mode_scan(strengths=None):
    strengths = np.asarray(strengths if strengths is not None else np.linspace(0, 1, 16), dtype=float)
    qs_residual = 0.012 + 0.16 * strengths**2
    aspect = 6.0 - 0.35 * strengths + 0.2 * strengths**2
    return strengths, qs_residual, aspect
