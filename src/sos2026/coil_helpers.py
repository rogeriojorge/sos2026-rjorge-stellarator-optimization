from __future__ import annotations

import numpy as np
import pandas as pd


def coil_curves(stage: str = "initial", ncoils: int = 8, npts: int = 220):
    """Return compact modular coil loops distributed around the torus.

    Each coil is a closed loop near one toroidal station. The small toroidal
    excursion gives a realistic modular-coil lean without creating a helical
    winding that wraps continuously around the device.
    """
    u = np.linspace(0, 2 * np.pi, npts)
    curves = []
    radial_size = 0.27 if stage == "initial" else 0.23
    vertical_size = 0.44 if stage == "initial" else 0.39
    toroidal_lean = 0.13 if stage == "initial" else 0.09
    center_radius = 1.18 if stage == "initial" else 1.12
    scallop = 0.08 if stage == "initial" else 0.045
    for k in range(ncoils):
        phi0 = 2 * np.pi * k / ncoils
        phase = 0.55 * np.sin(2 * phi0)
        r = center_radius + radial_size * np.cos(u) + scallop * np.cos(2 * u + phase)
        phi = phi0 + toroidal_lean * np.sin(u) + 0.018 * np.sin(3 * u + phase)
        z = vertical_size * np.sin(u) + 0.06 * np.sin(2 * u + phase)
        x = r * np.cos(phi)
        y = r * np.sin(phi)
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
