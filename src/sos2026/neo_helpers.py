from __future__ import annotations

import numpy as np


def epsilon_eff_curves(n: int = 80):
    s = np.linspace(0.03, 1.0, n)
    hsx = 0.006 + 0.020 * s**2 + 0.002 * np.sin(2 * np.pi * s)
    w7x = 0.004 + 0.014 * s**1.7 + 0.0015 * np.cos(2 * np.pi * s)
    classical = 0.025 + 0.060 * s**1.2
    return {"s": s, "HSX QHS cached metric": hsx, "W7-X standard cached metric": w7x, "classical stellarator reference": classical}


def epsilon_sensitivity(strengths=None):
    strengths = np.asarray(strengths if strengths is not None else np.linspace(0, 1, 20), dtype=float)
    eps = 0.008 + 0.055 * strengths**2
    return strengths, eps
