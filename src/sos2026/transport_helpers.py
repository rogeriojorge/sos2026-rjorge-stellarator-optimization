from __future__ import annotations

import numpy as np


def sfincs_like_curves(n: int = 80):
    nu = np.logspace(-4, 0, n)
    d11 = 0.22 / np.sqrt(nu + 0.003) + 0.3 * nu
    d11_suppressed = d11 / (1 + 18 * np.exp(-((np.log10(nu) + 2.2) / 0.8) ** 2))
    er = np.linspace(-2.5, 2.5, n)
    ambipolar = er**3 - 1.2 * er + 0.2
    s = np.linspace(0, 1, n)
    bootstrap = 0.08 * s * (1 - s) * (1 + 0.25 * np.cos(2 * np.pi * s))
    return {"nu": nu, "D11_no_Er": d11, "D11_with_Er": d11_suppressed, "Er": er, "ambipolar": ambipolar, "s": s, "bootstrap": bootstrap}


def profile_closure(n: int = 100):
    r = np.linspace(0, 1, n)
    source = np.exp(-5 * r**2)
    chi_base = 0.25 + 0.15 * r**2
    chi_turb = chi_base + 0.65 * np.exp(-((r - 0.45) / 0.22) ** 2)
    ti_base = 1.0 + 3.0 * (1 - r**1.7) / (1 + 1.2 * chi_base)
    ti_turb = 1.0 + 3.0 * (1 - r**1.7) / (1 + 1.2 * chi_turb)
    te = 0.9 + 2.4 * (1 - r**1.9) / (1 + 0.8 * chi_base)
    flux_balance = source - np.gradient(chi_base * np.gradient(ti_base, r), r)
    return {"r": r, "source": source, "chi_base": chi_base, "chi_turb": chi_turb, "Ti_base": ti_base, "Ti_turbulent": ti_turb, "Te": te, "flux_balance": flux_balance}
