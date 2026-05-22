from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import imageio.v2 as imageio

from .paths import MOVIE_DIR, ensure_directories
from .vmec_helpers import synthetic_surface
from .coil_helpers import coil_curves


def _frame_from_figure(fig):
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    return rgba[..., :3].copy()


def rotating_surface_gif(path: Path | None = None, frames: int = 28) -> Path:
    ensure_directories()
    path = path or (MOVIE_DIR / "rotating_surface.gif")
    surface = synthetic_surface("hsx", ntheta=42, nphi=70)
    imgs = []
    for azim in np.linspace(0, 360, frames, endpoint=False):
        fig = plt.figure(figsize=(5.2, 4.0))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(surface["x"], surface["y"], surface["z"], cmap="viridis", linewidth=0, antialiased=True)
        for curve in coil_curves("final", ncoils=4, npts=120):
            ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], color="#111827", lw=1.0, alpha=0.75)
        ax.set_axis_off()
        ax.set_title("Cached rotating surface and coils", fontsize=11)
        ax.view_init(elev=22, azim=float(azim))
        imgs.append(_frame_from_figure(fig))
        plt.close(fig)
    imageio.mimsave(path, imgs, duration=0.08)
    return path


def optimization_history_gif(path: Path | None = None, frames: int = 30) -> Path:
    ensure_directories()
    path = path or (MOVIE_DIR / "optimization_history.gif")
    theta = np.linspace(0, 2 * np.pi, 120)
    zeta = np.linspace(0, 2 * np.pi, 120)
    tt, zz = np.meshgrid(theta, zeta, indexing="ij")
    imgs = []
    for k in range(frames):
        amp = 1.0 * np.exp(-k / 12) + 0.12
        err = amp * (np.sin(2 * tt - 3 * zz) + 0.4 * np.cos(3 * tt + zz))
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
        im = ax.imshow(err, origin="lower", cmap="coolwarm", vmin=-1.4, vmax=1.4, aspect="auto")
        ax.set_title(f"Normal-field error during toy optimization: step {k:02d}", fontsize=10)
        ax.set_xlabel("zeta index")
        ax.set_ylabel("theta index")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        imgs.append(_frame_from_figure(fig))
        plt.close(fig)
    imageio.mimsave(path, imgs, duration=0.09)
    return path
