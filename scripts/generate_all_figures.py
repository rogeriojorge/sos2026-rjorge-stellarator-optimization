from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import hashlib
import json
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sos2026.paths import CACHE_DIR, STATUS_DIR, FIGURE_DIR, PROJECT_ROOT, ensure_directories
from sos2026.plotting import PALETTE, savefig, caption, frame_3d_axes, plot_surface_3d, plot_iota_profile, plot_boozer_contour, plot_boozer_spectrum
from sos2026.vmec_helpers import synthetic_surface, load_iota_profile, boundary_mode_scan
from sos2026.boozer_helpers import synthetic_boozer_modes, compute_boozer_grid, symmetry_residual
from sos2026.neo_helpers import epsilon_eff_curves, epsilon_sensitivity
from sos2026.coil_helpers import coil_curves, normal_field_error, tradeoff_table
from sos2026.transport_helpers import sfincs_like_curves, profile_closure
from sos2026.turbulence_helpers import growth_rate_spectrum, proxy_validation_table, clamping_cartoon
from sos2026.pareto import design_table, nondominated, weighted_selection


def plot_environment():
    x = np.linspace(0, 1, 50)
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(x, np.sin(2 * np.pi * x), color=PALETTE["teal"], lw=2)
    ax.set_title("Environment figure write check")
    ax.set_xlabel("x")
    ax.set_ylabel("sin(2 pi x)")
    ax.grid(alpha=0.25)
    caption(ax, "If this file exists, matplotlib can write to assets/figures in cached mode.")
    return savefig(fig, "environment_check.png")


def plot_epsilon():
    data = epsilon_eff_curves()
    np.savez(CACHE_DIR / "epsilon_eff_comparison.npz", **data, source="synthetic educational fallback")
    fig, ax = plt.subplots(figsize=(6.5, 4.1))
    for key, val in data.items():
        if key != "s":
            ax.plot(data["s"], val, lw=2.3, label=key)
    ax.set_yscale("log")
    ax.set_xlabel("s")
    ax.set_ylabel("epsilon_eff proxy")
    ax.set_title("Effective-ripple comparison")
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.25)
    caption(ax, "Lower curves represent better low-collisionality neoclassical optimization in this screening metric.")
    savefig(fig, "03_epsilon_eff_comparison.png")

    strengths, eps = epsilon_sensitivity()
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(strengths, eps, marker="o", color=PALETTE["red"], lw=2)
    ax.set_xlabel("symmetry-breaking perturbation amplitude")
    ax.set_ylabel("epsilon_eff proxy")
    ax.set_title("Finite-difference sensitivity cartoon")
    ax.grid(alpha=0.25)
    ax.annotate("small symmetry-breaking changes can dominate the objective", xy=(strengths[-2], eps[-2]), xytext=(0.18, 0.75), textcoords="axes fraction", arrowprops={"arrowstyle": "->", "color": PALETTE["red"]}, fontsize=8.5, color=PALETTE["ink"])
    caption(ax, "Read this as gradient intuition; quantitative claims require a validated transport calculation.")
    savefig(fig, "03_epsilon_eff_sensitivity.png")


def plot_coils():
    surface = synthetic_surface("hsx", ntheta=36, nphi=64)
    for stage, name in [("initial", "04_initial_coils.png"), ("final", "04_final_coils.png")]:
        fig = plt.figure(figsize=(7.0, 3.9))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(
            surface["x"],
            surface["y"],
            surface["z"],
            color="#60a5fa",
            linewidth=0,
            alpha=0.54,
            shade=True,
            rstride=2,
            cstride=2,
        )
        for curve in coil_curves(stage):
            ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=3.2)
        frame_3d_axes(ax, None, elev=24, azim=32, zoom=2.08, rect=(-0.10, -0.20, 1.23, 1.26))
        savefig(fig, name)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), sharex=True, sharey=True)
    for ax, stage in zip(axes, ["initial", "final"]):
        theta, zeta, err = normal_field_error(stage)
        im = ax.contourf(zeta, theta, err, levels=24, cmap="coolwarm")
        ax.set_title(stage)
        ax.set_xlabel("zeta")
        ax.set_ylabel("theta")
    fig.colorbar(im, ax=axes.ravel().tolist(), label="B dot n proxy")
    axes[0].text(0, -0.22, "Before/after maps show whether the coil set preserves the target surface.", transform=axes[0].transAxes, fontsize=9, color=PALETTE["gray"])
    savefig(fig, "04_bdotn_before_after.png")
    table = tradeoff_table()
    table.to_csv(CACHE_DIR / "coil_demo_cached.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.1, 4.0))
    ax.plot(table["coil_length"], table["quadratic_flux"], marker="o", lw=2, color=PALETTE["blue"])
    ax.set_xlabel("normalized coil length")
    ax.set_ylabel("quadratic flux proxy")
    ax.set_title("Coil regularization tradeoff")
    ax.grid(alpha=0.25)
    ax.annotate("too much shortening\ncan worsen the field", xy=(table["coil_length"].iloc[-1], table["quadratic_flux"].iloc[-1]), xytext=(0.42, 0.70), textcoords="axes fraction", arrowprops={"arrowstyle": "->", "color": PALETTE["red"]}, fontsize=8.5, color=PALETTE["ink"])
    caption(ax, "Shorter coils can make the target field worse; this is why stage-2 design is multiobjective.")
    savefig(fig, "04_coil_tradeoff.png")


def plot_single_stage():
    k = np.arange(40)
    plasma = 0.6 * np.exp(-k / 9) + 0.04
    coil = 0.9 * np.exp(-k / 14) + 0.08
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(k, plasma, label="plasma metric")
    ax.plot(k, coil, label="coil metric")
    ax.set_xlabel("continuation step")
    ax.set_ylabel("objective contribution")
    ax.set_title("Single-stage toy objective history")
    ax.legend()
    ax.grid(alpha=0.25)
    caption(ax, "Continuation reduces competing terms together instead of optimizing a boundary first and coils later.")
    savefig(fig, "05_single_stage_history.png")
    w = np.logspace(-2, 1, 40)
    flux = 0.12 + 0.8 / (1 + 3 * w)
    complexity = 0.8 + 0.25 * np.log10(1 + 8 * w)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(w, flux, label="flux mismatch")
    ax.plot(w, complexity, label="coil complexity")
    ax.set_xscale("log")
    ax.set_xlabel("flux penalty weight")
    ax.set_ylabel("normalized metric")
    ax.set_title("Weight continuation")
    ax.legend()
    ax.grid(alpha=0.25)
    caption(ax, "Changing weights reveals which objective is currently controlling the design.")
    savefig(fig, "05_weight_continuation.png")


def plot_fieldlines_particles():
    t = np.linspace(0, 18 * np.pi, 1200)
    r = 1 + 0.18 * np.cos(0.22 * t)
    x = r * np.cos(t / 4)
    y = r * np.sin(t / 4)
    z = 0.16 * np.sin(t)
    surface = synthetic_surface("hsx", ntheta=28, nphi=48)
    fig = plt.figure(figsize=(7.0, 3.9))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(
        surface["x"],
        surface["y"],
        surface["z"],
        color="#60a5fa",
        linewidth=0,
        alpha=0.52,
        shade=True,
        rstride=2,
        cstride=2,
    )
    ax.plot(x, y, z, color=PALETTE["teal"], lw=2.2)
    frame_3d_axes(ax, None, elev=23, azim=31, zoom=2.65, rect=(-0.14, -0.24, 1.31, 1.34))
    savefig(fig, "06_fieldlines.png")
    t = np.linspace(0, 2 * np.pi, 300)
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    ax.plot(np.cos(t), np.sin(t), color=PALETTE["gray"], lw=2, label="confined orbit")
    ax.plot(0.75 * np.cos(t) + 0.25 * t / np.pi, 0.55 * np.sin(t), color=PALETTE["red"], lw=2, label="loss cartoon")
    ax.set_aspect("equal")
    ax.set_title("Particle-orbit confinement cartoon")
    ax.legend(fontsize=8)
    caption(ax, "Fast-particle diagnostics become reactor gates even when the fieldline picture looks acceptable.")
    savefig(fig, "06_particle_orbit.png")


def plot_sfincs_transport():
    d = sfincs_like_curves()
    np.savez(CACHE_DIR / "sfincs_demo_cached.npz", **d, source="synthetic educational fallback")
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.loglog(d["nu"], d["D11_no_Er"], label="without Er suppression")
    ax.loglog(d["nu"], d["D11_with_Er"], label="with Er suppression")
    ax.set_xlabel("collisionality proxy")
    ax.set_ylabel("D11-like coefficient")
    ax.set_title("Neoclassical D11 scan")
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.25)
    caption(ax, "Read this as the shape of a validation scan; quantitative claims require a production SFINCS_JAX solve.")
    savefig(fig, "07_sfincs_d11_scan.png")
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(d["Er"], d["ambipolar"], color=PALETTE["red"], lw=2)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("radial electric field proxy")
    ax.set_ylabel("ion flux - electron flux")
    ax.set_title("Ambipolar Er roots")
    ax.grid(alpha=0.25)
    caption(ax, "Roots mark candidate ambipolar electric fields that can change impurity and turbulence behavior.")
    savefig(fig, "07_er_roots.png")
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(d["s"], d["bootstrap"], color=PALETTE["teal"], lw=2)
    ax.set_xlabel("s")
    ax.set_ylabel("bootstrap-current proxy")
    ax.set_title("Bootstrap-current constraint")
    ax.grid(alpha=0.25)
    caption(ax, "Bootstrap current is a profile-dependent constraint, not just a geometry score.")
    savefig(fig, "07_bootstrap_profile.png")


def plot_turbulence():
    ky, gamma, omega = growth_rate_spectrum()
    np.savez(CACHE_DIR / "spectrax_linear_cached.npz", ky=ky, gamma=gamma, omega=omega, source="synthetic educational fallback")
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(ky, gamma, lw=2, color=PALETTE["red"])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("ky rho_i")
    ax.set_ylabel("growth rate proxy")
    ax.set_title("Linear turbulence metric")
    ax.grid(alpha=0.25)
    caption(ax, "Positive growth flags instability, but nonlinear heat flux can rank designs differently.")
    savefig(fig, "08_growth_rate_spectrum.png")
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(ky, omega, lw=2, color=PALETTE["blue"])
    ax.set_xlabel("ky rho_i")
    ax.set_ylabel("frequency proxy")
    ax.set_title("Linear mode frequency")
    ax.grid(alpha=0.25)
    caption(ax, "Frequency helps identify branches; it is not itself a confinement metric.")
    savefig(fig, "08_frequency_spectrum.png")
    table = proxy_validation_table()
    table.to_csv(CACHE_DIR / "turbulence_proxy_cached.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    x = np.arange(len(table))
    ax.plot(x, table["linear_proxy"], marker="o", label="linear proxy")
    ax.plot(x, table["quasilinear_proxy"], marker="o", label="quasilinear proxy")
    ax.plot(x, table["nonlinear_validation"], marker="o", label="nonlinear validation")
    ax.set_xticks(x, ["A_QS", "B_low", "C_coils", "D_valid", "E_bal", "F_fast"], rotation=20, ha="right")
    ax.set_ylabel("normalized heat-flux-like metric")
    ax.set_title("Proxy vs nonlinear validation")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    best_proxy = int(np.argmin(table["linear_proxy"].to_numpy()))
    best_valid = int(np.argmin(table["nonlinear_validation"].to_numpy()))
    ax.scatter([best_proxy], [table["linear_proxy"].iloc[best_proxy]], s=110, facecolors="none", edgecolors=PALETTE["red"], linewidths=2)
    ax.scatter([best_valid], [table["nonlinear_validation"].iloc[best_valid]], s=120, facecolors="none", edgecolors=PALETTE["green"], linewidths=2)
    ax.annotate("proxy winner", xy=(best_proxy, table["linear_proxy"].iloc[best_proxy]), xytext=(0.58, 0.22), textcoords="axes fraction", arrowprops={"arrowstyle": "->", "color": PALETTE["red"]}, fontsize=8.5)
    ax.annotate("validation winner", xy=(best_valid, table["nonlinear_validation"].iloc[best_valid]), xytext=(0.50, 0.78), textcoords="axes fraction", arrowprops={"arrowstyle": "->", "color": PALETTE["green"]}, fontsize=8.5)
    caption(ax, "The best proxy design is not always the best validation design; this is the optimizer's trap.")
    savefig(fig, "09_proxy_vs_nonlinear.png")
    p, neo, turb = clamping_cartoon()
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(p, neo, label="neoclassical-limited expectation")
    ax.plot(p, turb, label="turbulence-clamped cartoon")
    ax.set_xlabel("heating power proxy")
    ax.set_ylabel("ion-temperature proxy")
    ax.set_title("W7-X ion-temperature clamping cartoon")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    caption(ax, "A geometry can pass neoclassical gates and still need turbulence-aware validation.")
    savefig(fig, "09_w7x_clamping_cartoon.png")


def plot_profiles_pareto():
    d = profile_closure()
    np.savez(CACHE_DIR / "neopax_profile_cached.npz", **d, metadata_source="synthetic radial-transport fallback")
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(d["r"], d["Ti_base"], label="Ti baseline")
    ax.plot(d["r"], d["Ti_turbulent"], label="Ti with extra turbulent chi")
    ax.plot(d["r"], d["Te"], label="Te")
    ax.set_xlabel("r/a")
    ax.set_ylabel("temperature proxy")
    ax.set_title("Profile closure response")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    caption(ax, "The field design is not complete until profiles and sources close the transport loop.")
    savefig(fig, "10_profile_evolution.png")
    fig, ax = plt.subplots(figsize=(6.1, 3.8))
    ax.plot(d["r"], d["source"], label="source")
    ax.plot(d["r"], d["flux_balance"], label="residual")
    ax.set_xlabel("r/a")
    ax.set_ylabel("normalized power density")
    ax.set_title("Power-balance check")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    caption(ax, "A residual plot teaches whether the assumed transport closes with the chosen source.")
    savefig(fig, "10_power_balance.png")
    df = design_table()
    df.to_csv(CACHE_DIR / "pareto_design_table.csv", index=False)
    keep = nondominated(df, ["epsilon_eff", "coil_length", "turbulence_proxy"])
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.scatter(df["coil_length"], df["epsilon_eff"], c=df["turbulence_proxy"], s=90, cmap="plasma", edgecolor="black", linewidth=0.5)
    ax.scatter(df.loc[keep, "coil_length"], df.loc[keep, "epsilon_eff"], facecolors="none", edgecolors="lime", s=180, linewidths=2, label="nondominated")
    for _, row in df.iterrows():
        ax.text(row["coil_length"] + 0.01, row["epsilon_eff"], row["design"], fontsize=7)
    ax.set_xlabel("coil length proxy")
    ax.set_ylabel("epsilon_eff proxy")
    ax.set_title("Pareto front: transport vs coils")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    caption(ax, "Nondominated points expose tradeoffs that a single weighted objective can hide.")
    savefig(fig, "11_pareto_front.png")
    ranked = weighted_selection(df, {"epsilon_eff": 0.35, "coil_length": 0.25, "turbulence_proxy": 0.25, "profile_error": 0.15})
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.bar(ranked["design"], ranked["weighted_score"], color=PALETTE["teal"])
    ax.set_ylabel("weighted score, lower is better")
    ax.set_title("Weighted selection dashboard")
    ax.tick_params(axis="x", rotation=30)
    caption(ax, "Changing weights is a design decision, not a physics result.")
    savefig(fig, "11_weighted_selection.png")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


FIGURE_PROVENANCE = {
    "01_hsx_surface.png": ("synthetic educational fallback", "scripts/generate_all_figures.py", ["Lecture 1", "notebooks/01_vmec_jax_first_equilibrium.ipynb"]),
    "01_w7x_surface.png": ("synthetic educational fallback", "scripts/generate_all_figures.py", ["Lecture 1"]),
    "01_iota_profile.png": ("real public data", "data/vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc when present", ["Lecture 1", "notebooks/01_vmec_jax_first_equilibrium.ipynb"]),
    "02_boozer_contour.png": ("synthetic educational fallback", "src/sos2026/boozer_helpers.py", ["Lecture 1", "notebooks/02_boozer_spectrum.ipynb"]),
    "02_boozer_spectrum.png": ("synthetic educational fallback", "src/sos2026/boozer_helpers.py", ["Lecture 1", "notebooks/02_boozer_spectrum.ipynb"]),
    "03_epsilon_eff_comparison.png": ("cached derived data", "data/cached/epsilon_eff_comparison.npz", ["Lecture 1", "Lecture 3", "notebooks/03_effective_ripple_neo_jax.ipynb"]),
    "03_epsilon_eff_sensitivity.png": ("synthetic educational fallback", "src/sos2026/neo_helpers.py", ["Lecture 1", "notebooks/03_effective_ripple_neo_jax.ipynb"]),
    "04_initial_coils.png": ("synthetic educational fallback", "src/sos2026/coil_helpers.py", ["Lecture 2", "notebooks/04_simsopt_stage2_coils.ipynb"]),
    "04_final_coils.png": ("synthetic educational fallback", "src/sos2026/coil_helpers.py", ["Lecture 2", "notebooks/04_simsopt_stage2_coils.ipynb"]),
    "04_bdotn_before_after.png": ("synthetic educational fallback", "src/sos2026/coil_helpers.py", ["Lecture 2", "notebooks/04_simsopt_stage2_coils.ipynb"]),
    "04_coil_tradeoff.png": ("cached derived data", "data/cached/coil_demo_cached.csv", ["Lecture 2", "notebooks/04_simsopt_stage2_coils.ipynb"]),
    "06_fieldlines.png": ("synthetic educational fallback", "scripts/generate_all_figures.py", ["Lecture 2", "notebooks/06_essos_fieldlines_particles.ipynb"]),
    "06_particle_orbit.png": ("synthetic educational fallback", "scripts/generate_all_figures.py", ["Lecture 2", "notebooks/06_essos_fieldlines_particles.ipynb"]),
    "07_sfincs_d11_scan.png": ("cached derived data", "data/cached/sfincs_demo_cached.npz", ["Lecture 3", "notebooks/07_sfincs_jax_neoclassical_cached.ipynb"]),
    "07_er_roots.png": ("cached derived data", "data/cached/sfincs_demo_cached.npz", ["Lecture 3", "notebooks/07_sfincs_jax_neoclassical_cached.ipynb"]),
    "07_bootstrap_profile.png": ("cached derived data", "data/cached/sfincs_demo_cached.npz", ["Lecture 3", "notebooks/07_sfincs_jax_neoclassical_cached.ipynb"]),
    "08_growth_rate_spectrum.png": ("cached derived data", "data/cached/spectrax_linear_cached.npz", ["Lecture 3", "notebooks/08_spectrax_gk_linear_metric.ipynb"]),
    "08_frequency_spectrum.png": ("cached derived data", "data/cached/spectrax_linear_cached.npz", ["Lecture 3", "notebooks/08_spectrax_gk_linear_metric.ipynb"]),
    "09_proxy_vs_nonlinear.png": ("cached derived data", "data/cached/turbulence_proxy_cached.csv", ["Lecture 3", "notebooks/09_turbulence_metric_surrogate.ipynb"]),
    "09_w7x_clamping_cartoon.png": ("synthetic educational fallback", "src/sos2026/turbulence_helpers.py", ["Lecture 3"]),
    "10_profile_evolution.png": ("cached derived data", "data/cached/neopax_profile_cached.npz", ["Lecture 4", "notebooks/10_neopax_profile_closure.ipynb"]),
    "10_power_balance.png": ("cached derived data", "data/cached/neopax_profile_cached.npz", ["Lecture 4", "notebooks/10_neopax_profile_closure.ipynb"]),
    "11_pareto_front.png": ("cached derived data", "data/cached/pareto_design_table.csv", ["Lecture 4", "notebooks/11_pareto_design_dashboard.ipynb"]),
    "11_weighted_selection.png": ("cached derived data", "data/cached/pareto_design_table.csv", ["Lecture 4", "notebooks/11_pareto_design_dashboard.ipynb"]),
}


def write_figure_manifest() -> Path:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    warning = "This cached figure teaches how to read the metric. It is not a new validated transport, coil, or equilibrium calculation."
    reference_sources_path = FIGURE_DIR / "reference_slide_sources.json"
    reference_sources = {}
    if reference_sources_path.exists():
        for item in json.loads(reference_sources_path.read_text(encoding="utf-8")):
            reference_sources[Path(item["file"]).name] = item
    for path in sorted(FIGURE_DIR.glob("*.png")):
        if path.name in reference_sources:
            ref = reference_sources[path.name]
            category = "reference slide extract"
            source = f"{ref['source_pdf']} slide {ref['source_slide']}: {ref['description']}"
            used_by = ["PowerPoint lecture decks"]
            figure_warning = "This is a selected visual extract from local reference teaching material, used with source attribution."
        else:
            category, source, used_by = FIGURE_PROVENANCE.get(path.name, ("synthetic educational fallback", "scripts/generate_all_figures.py", ["supporting documentation"]))
            figure_warning = warning if category != "real public data" else "This figure uses a real public input artifact but may still include cached plotting choices."
        records.append({
            "path": str(path.relative_to(PROJECT_ROOT)),
            "category": category,
            "source": source,
            "generated_at": generated_at,
            "sha256": file_sha256(path),
            "used_by": used_by,
            "warning": figure_warning,
        })
    manifest = {
        "schema": "sos2026.figure-manifest/v1",
        "generated_at": generated_at,
        "categories": ["real public data", "real package output", "cached derived data", "synthetic educational fallback", "reference slide extract"],
        "figures": records,
    }
    path = FIGURE_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ensure_directories()
    paths = []
    paths.append(plot_environment())
    paths.append(plot_surface_3d(synthetic_surface("hsx"), "HSX-like QHS surface", "01_hsx_surface.png"))
    paths.append(plot_surface_3d(synthetic_surface("w7x"), "W7-X-like reference surface", "01_w7x_surface.png"))
    s, iota, _ = load_iota_profile()
    paths.append(plot_iota_profile(s, iota))
    modes = synthetic_boozer_modes("hsx")
    theta, zeta, b = compute_boozer_grid(modes)
    np.savez(CACHE_DIR / "boozer_hsx_synthetic_or_real.npz", theta=theta, zeta=zeta, B=b, **modes, residual=symmetry_residual(modes), source="synthetic educational fallback")
    paths.append(plot_boozer_contour(theta, zeta, b))
    paths.append(plot_boozer_spectrum(modes))
    strengths, qs, aspect = boundary_mode_scan()
    np.savez(CACHE_DIR / "boundary_mode_scan_cached.npz", strength=strengths, qs_residual=qs, aspect=aspect, source="synthetic educational fallback")
    plot_epsilon()
    plot_coils()
    plot_single_stage()
    plot_fieldlines_particles()
    plot_sfincs_transport()
    plot_turbulence()
    plot_profiles_pareto()
    manifest = write_figure_manifest()
    figures = sorted(str(p.name) for p in (ROOT / "assets" / "figures").glob("*.png"))
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "figures.json").write_text(json.dumps({"count": len(figures), "figures": figures, "manifest": str(manifest.relative_to(PROJECT_ROOT))}, indent=2), encoding="utf-8")
    print(f"Generated {len(figures)} figures in assets/figures")
    return 0 if len(figures) >= 8 else 2


if __name__ == "__main__":
    raise SystemExit(main())
