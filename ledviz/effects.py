"""The three visuals. Each effect is a pure function frame(i, n) -> (64, 64, 3) uint8.

Every effect is periodic in i with period n, so the GIF loops with no visible seam:
frame(n, n) == frame(0, n). The tests assert it.
"""
from __future__ import annotations

import numpy as np

from .core import SIZE, X, Y, gradient, to_frame

TAU = 2 * np.pi

# --------------------------------------------------------------------------- plasma
# Classic demoscene plasma: a sum of sines, mapped through a cycling palette.
PLASMA_PALETTE = gradient([
    (0.00, (10, 0, 40)),
    (0.20, (120, 0, 160)),
    (0.40, (255, 40, 120)),
    (0.55, (255, 170, 30)),
    (0.70, (255, 255, 200)),
    (0.85, (30, 200, 255)),
    (1.00, (10, 0, 40)),   # wraps back to the start so the palette cycle is seamless
])


def plasma(i: int, n: int) -> np.ndarray:
    t = TAU * i / n  # every time term below uses an integer multiple of t -> periodic
    cx = 0.6 * np.sin(t)
    cy = 0.6 * np.cos(2 * t)
    v = (
        np.sin(X * 5 + t)
        + np.sin((Y * 4 - t) + np.sin(X * 2 + t))
        + np.sin(np.hypot(X - cx, Y - cy) * 9 - 2 * t)
        + np.sin((X + Y) * 3 + np.cos(t))
    )
    idx = ((v + 4) / 8 + i / n) % 1.0            # palette scrolls one full turn per loop
    return PLASMA_PALETTE[(idx * 255).astype(int)]


# --------------------------------------------------------------------------- warp
# Hyperspace starfield: stars fly toward the viewer and leave streaks.
_rng = np.random.default_rng(40_000)
_N_STARS = 260
_star_xy = _rng.uniform(-1, 1, (_N_STARS, 2))
_star_z0 = _rng.uniform(0, 1, _N_STARS)
_star_hue = _rng.choice(3, _N_STARS, p=[0.6, 0.25, 0.15])
_STAR_COLOURS = np.array([(200, 230, 255), (120, 170, 255), (255, 210, 150)], dtype=float)
_WARP_LAPS = 1  # each star crosses the depth range exactly once per loop


def _project(xy: np.ndarray, z: np.ndarray) -> np.ndarray:
    depth = 0.04 + z
    return xy / depth[:, None] * 0.18 * SIZE / 2 + SIZE / 2


def warp(i: int, n: int) -> np.ndarray:
    img = np.zeros((SIZE, SIZE, 3))
    # faint blue vortex in the centre
    r = np.hypot(X, Y)
    img[..., 2] += 40 * np.exp(-r * 4)
    img[..., 0] += 10 * np.exp(-r * 6)

    phase = i / n * _WARP_LAPS
    z = (_star_z0 - phase) % 1.0                 # 1 = far, 0 = at the viewer
    z_tail = np.minimum(z + 0.06, 1.0)
    head = _project(_star_xy, z)
    tail = _project(_star_xy, z_tail)
    bright = np.clip((0.9 - z) / 0.9, 0, 1) ** 2.4  # distant stars fade out, no centre blob

    for k in range(_N_STARS):
        steps = 8
        for s in range(steps + 1):
            f = s / steps
            px, py = tail[k] + (head[k] - tail[k]) * f
            xi, yi = int(px), int(py)
            if 0 <= xi < SIZE and 0 <= yi < SIZE:
                img[yi, xi] += _STAR_COLOURS[_star_hue[k]] * bright[k] * (0.25 + 0.75 * f)
    return to_frame(img)


# --------------------------------------------------------------------------- globe
# A spinning pixel planet ("Terra") with continents, ice caps, clouds and a day/night line.
def _value_noise_3d(p: np.ndarray, seed: int, octaves: int = 4) -> np.ndarray:
    """Smooth 3D value noise sampled at points p (..., 3). Deterministic per seed."""
    rng = np.random.default_rng(seed)
    lattice = rng.random((32, 32, 32))
    total = np.zeros(p.shape[:-1])
    amp, freq, norm = 1.0, 2.0, 0.0
    for _ in range(octaves):
        q = p * freq + 16
        i0 = np.floor(q).astype(int)
        f = q - i0
        f = f * f * (3 - 2 * f)
        acc = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    w = (
                        (f[..., 0] if dx else 1 - f[..., 0])
                        * (f[..., 1] if dy else 1 - f[..., 1])
                        * (f[..., 2] if dz else 1 - f[..., 2])
                    )
                    acc = acc + w * lattice[(i0[..., 0] + dx) % 32, (i0[..., 1] + dy) % 32, (i0[..., 2] + dz) % 32]
        total += amp * acc
        norm += amp
        amp *= 0.5
        freq *= 2
    return total / norm


_R = 0.78
_rr = X ** 2 + Y ** 2
_DISK = _rr < _R ** 2
_SZ = np.sqrt(np.clip(_R ** 2 - _rr, 0, None)) / _R   # sphere normal z
_SX, _SY = X / _R, Y / _R
_LIGHT = np.array([-0.55, -0.35, 0.76])
_LIGHT /= np.linalg.norm(_LIGHT)
_SHADE = np.clip(_SX * _LIGHT[0] + _SY * _LIGHT[1] + _SZ * _LIGHT[2], 0, 1)
_TILT = np.deg2rad(18)

_bg_rng = np.random.default_rng(7)
_BG_STARS = np.zeros((SIZE, SIZE))
_BG_STARS[_bg_rng.integers(0, SIZE, 70), _bg_rng.integers(0, SIZE, 70)] = _bg_rng.uniform(0.3, 1, 70)

LAND = gradient([(0.0, (30, 110, 40)), (0.5, (120, 150, 50)), (0.8, (150, 110, 60)), (1.0, (230, 230, 230))])
SEA = gradient([(0.0, (5, 20, 80)), (1.0, (20, 90, 180))])


def _sphere_points(angle: float) -> np.ndarray:
    """Body-frame 3D points for each visible pixel when the planet is rotated by angle."""
    # undo axial tilt (rotate about view x), then undo spin (rotate about planet y)
    y1 = _SY * np.cos(_TILT) - _SZ * np.sin(_TILT)
    z1 = _SY * np.sin(_TILT) + _SZ * np.cos(_TILT)
    x2 = _SX * np.cos(angle) + z1 * np.sin(angle)
    z2 = -_SX * np.sin(angle) + z1 * np.cos(angle)
    return np.stack([x2, y1, z2], axis=-1)


def globe(i: int, n: int) -> np.ndarray:
    t = TAU * i / n
    img = np.zeros((SIZE, SIZE, 3))

    # starfield that twinkles with an integer number of cycles per loop
    twinkle = 0.6 + 0.4 * np.sin(3 * t + _BG_STARS * 40)
    img += (_BG_STARS * twinkle * 200)[..., None]

    p = _sphere_points(t)                       # one full turn per loop
    height = _value_noise_3d(p, seed=3)
    lat = np.abs(p[..., 1])
    land = height > 0.52
    sea_level = np.clip((height - 0.3) / 0.22, 0, 1)
    land_h = np.clip((height - 0.52) / 0.25, 0, 1)
    surf = np.where(land[..., None], LAND[(land_h * 255).astype(int)], SEA[(sea_level * 255).astype(int)]).astype(float)
    ice = lat > 0.82
    surf[ice] = (235, 245, 255)

    # clouds drift at twice the spin speed: still exactly periodic
    cp = _sphere_points(2 * t)
    clouds = np.clip((_value_noise_3d(cp * 1.3, seed=11, octaves=3) - 0.55) * 4, 0, 0.85)
    surf = surf * (1 - clouds[..., None]) + 255 * clouds[..., None]

    # lighting: day side lit, night side with tiny city lights on land
    lit = surf * (0.08 + 0.92 * _SHADE[..., None])
    night = (_SHADE < 0.05) & land & ~ice & (_value_noise_3d(p * 9, seed=5, octaves=1) > 0.78)
    lit[night] = (200, 140, 50)

    img[_DISK] = lit[_DISK]

    # atmosphere rim
    rim = np.exp(-((np.sqrt(_rr) - _R) / 0.05) ** 2) * (0.35 + 0.65 * np.clip(-X * 0.8 - Y * 0.5 + 0.6, 0, 1))
    img += rim[..., None] * np.array([60, 140, 255])
    return to_frame(img)


EFFECTS = {
    "plasma": (plasma, 96, 20),   # name: (fn, frames, fps)
    "warp": (warp, 40, 25),
    "terra": (globe, 120, 20),
}
