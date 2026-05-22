from __future__ import annotations

import numpy as np
import pandas as pd


def design_table() -> pd.DataFrame:
    return pd.DataFrame({
        "design": ["HSX-thread", "W7X-ref", "QA-coils", "QI-transport", "easy-coils", "balanced", "aggressive-QS", "profile-safe"],
        "qs_residual": [0.025, 0.040, 0.020, 0.032, 0.060, 0.030, 0.014, 0.038],
        "epsilon_eff": [0.018, 0.013, 0.021, 0.011, 0.036, 0.017, 0.015, 0.016],
        "coil_length": [1.15, 1.30, 1.42, 1.55, 0.92, 1.12, 1.68, 1.20],
        "curvature": [1.20, 1.32, 1.46, 1.60, 0.98, 1.18, 1.75, 1.25],
        "normal_field_error": [0.24, 0.18, 0.16, 0.22, 0.44, 0.20, 0.12, 0.25],
        "turbulence_proxy": [0.36, 0.28, 0.42, 0.30, 0.50, 0.26, 0.47, 0.24],
        "profile_error": [0.25, 0.22, 0.32, 0.24, 0.40, 0.20, 0.36, 0.18],
    })


def nondominated(df: pd.DataFrame, columns=None) -> np.ndarray:
    columns = columns or ["qs_residual", "epsilon_eff", "coil_length", "turbulence_proxy"]
    values = df[columns].to_numpy(float)
    keep = np.ones(len(values), dtype=bool)
    for i, row in enumerate(values):
        if not keep[i]:
            continue
        dominates = np.all(values <= row, axis=1) & np.any(values < row, axis=1)
        if np.any(dominates):
            keep[i] = False
    return keep


def weighted_selection(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    out = df.copy()
    score = np.zeros(len(out))
    for col, weight in weights.items():
        x = out[col].to_numpy(float)
        scaled = (x - x.min()) / (np.ptp(x) + 1e-12)
        score += weight * scaled
    out["weighted_score"] = score
    return out.sort_values("weighted_score")
