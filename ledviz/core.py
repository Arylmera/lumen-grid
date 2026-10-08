"""Shared helpers: the 64x64 grid and GIF export."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 64          # the LED matrix is 64x64
MAX_BYTES = 5 * 1024 * 1024  # contest limit per file


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


def stamp(c: np.ndarray, rows: list[str], top: int, left: int) -> None:
    """Paint an ASCII map into a char canvas; '.' is transparent; x wraps around the tile."""
    h, w = c.shape
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= top + r < h:
                c[top + r, (left + col) % w] = ch
