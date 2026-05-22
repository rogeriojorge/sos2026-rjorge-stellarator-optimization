from __future__ import annotations

import numpy as np


def synthetic_boozer_modes(case: str = "hsx") -> dict:
    if case.lower().startswith("w7"):
        nfp = 5
        rows = [(0, 0, 1.0), (1, 0, 0.055), (1, 5, 0.070), (2, 10, 0.025), (1, 4, 0.018), (2, 9, 0.014), (3, 15, 0.010)]
    else:
        nfp = 4
        rows = [(0, 0, 1.0), (1, 4, 0.090), (2, 8, 0.030), (3, 12, 0.012), (1, 3, 0.020), (2, 7, 0.014), (3, 11, 0.008)]
    return {
        "m": np.array([r[0] for r in rows], dtype=int),
        "n": np.array([r[1] for r in rows], dtype=int),
        "bmn": np.array([r[2] for r in rows], dtype=float),
        "nfp": nfp,
        "label": f"{case.upper()} synthetic/cached educational Boozer spectrum",
    }


def compute_boozer_grid(modes: dict, ntheta: int = 96, nzeta: int = 128):
    theta = np.linspace(0, 2 * np.pi, ntheta)
    zeta = np.linspace(0, 2 * np.pi / max(1, int(modes.get("nfp", 1))), nzeta)
    tt, zz = np.meshgrid(theta, zeta, indexing="ij")
    b = np.zeros_like(tt)
    for m, n, bmn in zip(modes["m"], modes["n"], modes["bmn"]):
        if int(m) == 0 and int(n) == 0:
            b = b + bmn
        else:
            b = b + bmn * np.cos(m * tt - n * zz)
    return theta, zeta, b


def symmetry_residual(modes: dict) -> float:
    nfp = int(modes.get("nfp", 1))
    total = 0.0
    bad = 0.0
    for m, n, b in zip(modes["m"], modes["n"], modes["bmn"]):
        if m == 0 and n == 0:
            continue
        total += abs(float(b))
        if nfp and (int(n) % nfp != 0):
            bad += abs(float(b))
    return bad / max(total, 1e-12)
