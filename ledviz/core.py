"""Shared helpers: the 64x64 grid, palettes, and GIF export."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 64          # the LED matrix is 64x64
MAX_BYTES = 5 * 1024 * 1024  # contest limit per file

# Pixel-centre coordinates in [-1, 1], shared by every effect.
_axis = (np.arange(SIZE) + 0.5) / SIZE * 2 - 1
X, Y = np.meshgrid(_axis, _axis)


def gradient(stops: list[tuple[float, tuple[int, int, int]]], n: int = 256) -> np.ndarray:
    """Build an (n, 3) uint8 palette by linear interpolation between colour stops."""
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    t = np.linspace(0, 1, n)
    return np.stack([np.interp(t, pos, cols[:, c]) for c in range(3)], axis=1).astype(np.uint8)


def to_frame(rgb: np.ndarray) -> np.ndarray:
    """Clip a float or int (64, 64, 3) array to a uint8 frame."""
    return np.clip(rgb, 0, 255).astype(np.uint8)


def save_gif(frames: list[np.ndarray], path: Path, fps: int = 20, scale: int = 1) -> Path:
    """Write a looping GIF. scale>1 upsizes with nearest-neighbour so pixels stay crisp."""
    images = [Image.fromarray(f, "RGB") for f in frames]
    if scale > 1:
        images = [im.resize((SIZE * scale, SIZE * scale), Image.NEAREST) for im in images]
    # One shared adaptive palette keeps colours stable from frame to frame (no GIF flicker).
    strip = Image.new("RGB", (images[0].width, images[0].height * len(images)))
    for i, im in enumerate(images):
        strip.paste(im, (0, i * im.height))
    pal = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    quantized = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in images]
    path.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        duration=round(1000 / fps),
        loop=0,
        optimize=False,
        disposal=1,
    )
    return path
