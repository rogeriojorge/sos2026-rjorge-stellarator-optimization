from __future__ import annotations

import warnings
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from .paths import FIGURE_DIR, ensure_directories

PALETTE = {
    "ink": "#1f2933",
    "blue": "#2563eb",
    "teal": "#0f766e",
    "red": "#b42318",
    "gold": "#b7791f",
    "gray": "#64748b",
    "green": "#2f855a",
}


def savefig(fig, name: str, dpi: int = 160) -> Path:
    ensure_directories()
    path = FIGURE_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="This figure includes Axes that are not compatible with tight_layout")
        fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    if "inline" not in plt.get_backend().lower():
        plt.close(fig)
    return path


def caption(ax, text: str) -> None:
    ax.text(0.0, -0.14, text, transform=ax.transAxes, fontsize=9, color=PALETTE["gray"], va="top")


def provenance_label(ax, label: str = "synthetic educational fallback") -> None:
    ax.text(
        0.995,
        0.01,
        label,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color=PALETTE["gray"],
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#e5e7eb", "alpha": 0.86},
    )


def fix_matplotlib_3d(ax) -> None:
    """Use equal data limits for a 3D Matplotlib axes."""
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])
    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass


def frame_3d_axes(
    ax,
    title: str | None = None,
    *,
    elev: float = 22,
    azim: float = 35,
    zoom: float = 2.25,
    rect: tuple[float, float, float, float] = (-0.10, -0.13, 1.20, 1.17),
) -> None:
    """Apply the shared SOS 3D framing: equal aspect, orthographic view, and tight use of the canvas."""
    if title:
        ax.figure.text(0.5, 0.965, title, ha="center", va="top", fontsize=15, color=PALETTE["ink"])
    ax.set_axis_off()
    try:
        ax.set_proj_type("ortho")
    except Exception:
        pass
    fix_matplotlib_3d(ax)
    try:
        ax.set_box_aspect((1, 1, 1), zoom=zoom)
    except TypeError:
        try:
            ax.dist = max(6.0, 10.0 / zoom)
        except Exception:
            pass
    except Exception:
        pass
    ax.view_init(elev=elev, azim=azim)
    ax.set_position(rect)


def plot_iota_profile(s, iota, title="Rotational transform profile", name="01_iota_profile.png"):
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(s, iota, color=PALETTE["blue"], lw=2.5)
    ax.set_xlabel("normalized toroidal flux s")
    ax.set_ylabel("iota")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    caption(ax, "Read this as the field-line pitch profile that an optimizer can target or constrain.")
    return savefig(fig, name)


def plot_surface_3d(surface: dict, title: str, name: str):
    fig = plt.figure(figsize=(7.0, 3.9))
    ax = fig.add_subplot(111, projection="3d")
    x, y, z = surface["x"], surface["y"], surface["z"]
    color = np.sqrt(x * x + y * y)
    ax.plot_surface(x, y, z, facecolors=plt.cm.viridis((color - color.min()) / (np.ptp(color) + 1e-12)), rstride=2, cstride=2, linewidth=0, antialiased=True, alpha=0.96)
    frame_3d_axes(ax, title, elev=22, azim=32, rect=(-0.04, -0.16, 1.12, 1.20))
    ax.figure.text(0.03, 0.86, "synthetic educational fallback", fontsize=8, color=PALETTE["gray"])
    return savefig(fig, name)


def plot_boozer_contour(theta, zeta, b, title="B(theta, zeta)", name="02_boozer_contour.png"):
    fig, ax = plt.subplots(figsize=(6.5, 4.3))
    c = ax.contourf(zeta, theta, b, levels=24, cmap="magma")
    fig.colorbar(c, ax=ax, label="|B| / <B>")
    ax.set_xlabel("Boozer toroidal angle zeta")
    ax.set_ylabel("Boozer poloidal angle theta")
    ax.set_title(title)
    caption(ax, "Bands aligned with the intended symmetry are cheap visual checks before scalar metrics.")
    return savefig(fig, name)


def plot_boozer_spectrum(modes, title="Boozer spectrum", name="02_boozer_spectrum.png"):
    mvals = sorted(set(int(v) for v in modes["m"]))
    nvals = sorted(set(int(v) for v in modes["n"]))
    grid = np.zeros((len(mvals), len(nvals)))
    for m, n, b in zip(modes["m"], modes["n"], modes["bmn"]):
        grid[mvals.index(int(m)), nvals.index(int(n))] = abs(float(b))
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    im = ax.imshow(grid, origin="lower", cmap="cividis", aspect="auto")
    ax.set_xticks(range(len(nvals)), nvals)
    ax.set_yticks(range(len(mvals)), mvals)
    ax.set_xlabel("toroidal mode n")
    ax.set_ylabel("poloidal mode m")
    ax.set_title(title)
    nfp = int(modes.get("nfp", 1))
    for m, n, b in zip(modes["m"], modes["n"], modes["bmn"]):
        if int(m) == 0 and int(n) == 0:
            continue
        row = mvals.index(int(m))
        col = nvals.index(int(n))
        good = nfp and int(n) % nfp == 0
        color = "#22c55e" if good else PALETTE["red"]
        ax.scatter(col, row, s=220 if good else 260, facecolors="none", edgecolors=color, linewidths=2.0)
    ax.text(0.02, 0.98, "green = symmetry line\nred = penalize", transform=ax.transAxes, fontsize=8.5, color=PALETTE["ink"], va="top", bbox={"facecolor": "white", "edgecolor": "#e5e7eb", "alpha": 0.88})
    fig.colorbar(im, ax=ax, label="|Bmn| / B00")
    caption(ax, "The sparse dominant line represents the intended symmetry; off-line modes become optimization penalties.")
    provenance_label(ax)
    return savefig(fig, name)
