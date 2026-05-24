from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont

from .paths import MOVIE_DIR, ensure_directories
from .plotting import frame_3d_axes
from .vmec_helpers import synthetic_surface
from .coil_helpers import coil_curves


def _frame_from_figure(fig):
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    return rgba[..., :3].copy()


def _first_frame_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}_first_frame.png")


def _storyboard_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}_storyboard.png")


def _write_storyboard(path: Path, imgs: list[np.ndarray], labels: list[str] | None = None) -> Path:
    frames = [Image.fromarray(img).resize((360, 238)) for img in imgs]
    labels = labels or [f"frame {i + 1}" for i in range(len(frames))]
    gap = 18
    label_h = 34
    width = len(frames) * 360 + (len(frames) + 1) * gap
    height = 238 + label_h + 2 * gap
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("Arial.ttf", 17)
    except Exception:
        font = ImageFont.load_default()
    for index, frame in enumerate(frames):
        x = gap + index * (360 + gap)
        canvas.paste(frame, (x, gap + label_h))
        draw.text((x, gap), labels[index], fill=(31, 41, 51), font=font)
        draw.rectangle((x, gap + label_h, x + 360, gap + label_h + 238), outline=(210, 210, 210), width=1)
    out = _storyboard_path(path)
    canvas.save(out)
    return out


def rotating_surface_gif(path: Path | None = None, frames: int = 28) -> Path:
    ensure_directories()
    path = path or (MOVIE_DIR / "rotating_surface.gif")
    surface = synthetic_surface("hsx", ntheta=42, nphi=70)
    imgs = []
    angles = np.linspace(0, 360, frames, endpoint=False)
    for azim in angles:
        fig = plt.figure(figsize=(6.2, 4.1))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(surface["x"], surface["y"], surface["z"], cmap="viridis", linewidth=0, antialiased=True)
        for curve in coil_curves("final", ncoils=8, npts=120):
            ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], color="#111827", lw=1.4, alpha=0.82)
        frame_3d_axes(ax, "Rotating surface and modular coils", elev=22, azim=float(azim), rect=(-0.08, -0.20, 1.18, 1.22))
        imgs.append(_frame_from_figure(fig))
        plt.close(fig)
    imageio.mimsave(path, imgs, duration=0.08)
    imageio.imwrite(_first_frame_path(path), imgs[0])
    picks = [0, frames // 4, frames // 2, 3 * frames // 4]
    _write_storyboard(path, [imgs[i] for i in picks], [f"view {int(angles[i]):03d} deg" for i in picks])
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
    imageio.imwrite(_first_frame_path(path), imgs[0])
    picks = [0, frames // 3, 2 * frames // 3, frames - 1]
    _write_storyboard(path, [imgs[i] for i in picks], [f"step {i:02d}" for i in picks])
    return path
