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


def blit(c: np.ndarray, rows: list[str], top: int, left: int, pal: dict | None = None) -> None:
    """stamp() without the x wrap: a screen-space sprite clips at the edges. With pal, each char
    is written as pal[char] (an RGB canvas); without it, as the char itself (a char canvas)."""
    h, w = c.shape[:2]
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= top + r < h and 0 <= left + col < w:
                c[top + r, left + col] = ch if pal is None else pal[ch]


def keyline(mask: np.ndarray) -> np.ndarray:
    """The mask grown by 1 px (4-neighbour): paint the result black, then the sprite over it,
    for a 1 px black outline that separates the sprite from whatever lies behind."""
    ring = mask.copy()
    ring[1:] |= mask[:-1]
    ring[:-1] |= mask[1:]
    ring[:, 1:] |= mask[:, :-1]
    ring[:, :-1] |= mask[:, 1:]
    return ring
