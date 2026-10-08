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


# --------------------------------------------------------------------------- drawing kit
# Integer pixel grid shared by every scene. CX is the vertical mirror line.
YY, XX = np.mgrid[0:SIZE, 0:SIZE].astype(float)
CX = (SIZE - 1) / 2
U = np.abs(XX - CX)            # distance from the mirror line: symmetric shapes test on U
TAU = 2 * np.pi


def ramp(colors, level: np.ndarray) -> np.ndarray:
    """Map a 0..1 level array through a list of RGB stops (evenly spaced)."""
    cols = np.asarray(colors, float)
    level = np.clip(level, 0, 1) * (len(cols) - 1)
    lo = np.floor(level).astype(int)
    hi = np.minimum(lo + 1, len(cols) - 1)
    f = (level - lo)[..., None]
    return cols[lo] * (1 - f) + cols[hi] * f


def dilate(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask, 1)
    return p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def edge(mask: np.ndarray) -> np.ndarray:
    """Mask pixels touching a non-mask pixel (4-neighbourhood): the shape's outline."""
    p = np.pad(mask, 1)
    return mask & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


def glow(img: np.ndarray, cy: float, cx: float, radius: float, rgb, strength: float) -> None:
    g = np.exp(-((XX - cx) ** 2 + (YY - cy) ** 2) / (2 * radius ** 2)) * strength
    img += g[..., None] * np.asarray(rgb, float)


def put(img: np.ndarray, y: float, x: float, rgb, a: float = 1.0) -> None:
    y, x = int(round(y)), int(round(x))
    if 0 <= y < SIZE and 0 <= x < SIZE:
        img[y, x] = img[y, x] * (1 - a) + np.asarray(rgb, float) * a


def sprite(rows: list[str], top: int, left: int, mirror: bool = False) -> dict[str, np.ndarray]:
    """ASCII art -> {char: mask}. '.' is transparent. mirror=True reflects the art about CX
    (draw only the left half, the rightmost column touching the centre line)."""
    out: dict[str, np.ndarray] = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "." or not (0 <= top + r < SIZE):
                continue
            m = out.setdefault(ch, np.zeros((SIZE, SIZE), bool))
            for x in ((left + c, SIZE - 1 - (left + c)) if mirror else (left + c,)):
                if 0 <= x < SIZE:
                    m[top + r, x] = True
    return out


def periodic_particles(seed: int, count: int, laps=(1, 2)):
    """Deterministic particles that each travel an integer number of laps per loop."""
    rng = np.random.default_rng(seed)
    return rng.uniform(0, SIZE, count), rng.uniform(0, SIZE, count), rng.choice(laps, count), rng.uniform(0, TAU, count)
