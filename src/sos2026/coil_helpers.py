from __future__ import annotations

import numpy as np
import pandas as pd


def coil_curves(stage: str = "initial", ncoils: int = 4, npts: int = 220):
    t = np.linspace(0, 2 * np.pi, npts)
    curves = []
    waviness = 0.12 if stage == "initial" else 0.07
    radius = 1.35 if stage == "initial" else 1.25
    for k in range(ncoils):
        phase = 2 * np.pi * k / ncoils
        r = radius + waviness * np.cos(3 * t + phase)
        x = r * np.cos(t + phase / 6)
        y = r * np.sin(t + phase / 6)
        z = 0.24 * np.sin(2 * t + phase) + (0.04 if stage == "initial" else 0.02) * np.sin(5 * t)
        curves.append(np.vstack([x, y, z]).T)
    return curves


def normal_field_error(stage: str = "initial", ntheta: int = 80, nzeta: int = 96):
    theta = np.linspace(0, 2 * np.pi, ntheta)
    zeta = np.linspace(0, 2 * np.pi, nzeta)
    tt, zz = np.meshgrid(theta, zeta, indexing="ij")
    amp = 1.0 if stage == "initial" else 0.28
    err = amp * (0.7 * np.sin(2 * tt - 3 * zz) + 0.35 * np.cos(3 * tt + zz) + 0.18 * np.sin(tt + 4 * zz))
    return theta, zeta, err


def tradeoff_table():
    return pd.DataFrame({
        "weight_length": [0.02, 0.05, 0.10, 0.20, 0.40],
        "quadratic_flux": [1.00, 0.58, 0.36, 0.31, 0.44],
        "coil_length": [1.32, 1.20, 1.10, 1.02, 0.96],
        "max_curvature": [1.55, 1.38, 1.24, 1.18, 1.16],
    })
