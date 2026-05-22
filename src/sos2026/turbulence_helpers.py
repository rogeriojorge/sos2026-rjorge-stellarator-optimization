from __future__ import annotations

import numpy as np
import pandas as pd


def growth_rate_spectrum(n: int = 60):
    ky = np.linspace(0.05, 1.6, n)
    gamma = 0.42 * ky * np.exp(-((ky - 0.55) / 0.45) ** 2) - 0.025
    omega = 0.55 * ky - 0.12 * ky**2
    return ky, gamma, omega


def proxy_validation_table():
    names = ["A_QS", "B_low_ripple", "C_easy_coils", "D_turbulence_checked", "E_balanced", "F_aggressive"]
    linear_proxy = np.array([0.22, 0.18, 0.42, 0.30, 0.26, 0.14])
    quasilinear = np.array([0.31, 0.28, 0.46, 0.23, 0.25, 0.34])
    nonlinear = np.array([0.50, 0.37, 0.54, 0.21, 0.27, 0.62])
    return pd.DataFrame({"design": names, "linear_proxy": linear_proxy, "quasilinear_proxy": quasilinear, "nonlinear_validation": nonlinear})


def clamping_cartoon(n: int = 80):
    power = np.linspace(0.5, 8.0, n)
    neoclassical = 1.0 + 0.42 * power**0.72
    turbulent = 1.0 + 0.95 * (1 - np.exp(-power / 2.2))
    return power, neoclassical, turbulent
