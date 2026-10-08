"""NECRON: an Overlord wakes in his tomb. The flesh is gone; the will remains.

Living-metal skull in brushed silver: domed cranium with a centre ridge, deep sockets where the
eyes burn gauss-green, nasal cavity, a grille of metal teeth. A striped nemes headdress with
energy running down its channels, a phylactery gem on the brow, ribbed collar plates and a
glowing core on the chest. Behind him, the tomb wall streams with falling glyphs. Twice a loop
the reanimation protocols glitch the picture.
"""
from __future__ import annotations

import numpy as np

from ..core import CX, SIZE, TAU, U, XX, YY, dilate, edge, glow, put, ramp, to_frame

SILVER = [(10, 12, 14), (45, 52, 56), (100, 110, 114), (165, 175, 178), (220, 230, 230), (255, 255, 250)]
GREEN = [(0, 20, 6), (0, 90, 25), (20, 200, 60), (120, 255, 140), (230, 255, 230)]
GUNMETAL = [(8, 10, 12), (26, 30, 34), (50, 56, 62), (85, 92, 100)]

# ------------------------------------------------------------------ geometry
_cran = ((U / 12) ** 2 + ((YY - 20) / 12.5) ** 2 <= 1) & (YY <= 30)
_jaw_hw = 11.8 - np.clip(YY - 29, 0, None) * 0.36
_jaw = (YY >= 26) & (YY <= 46) & (U <= _jaw_hw)
SKULL = _cran | _jaw
SKULL_EDGE = edge(SKULL)

_nx = (XX - CX) / 12
_ny = (YY - 27) / 20
_nz = np.sqrt(np.clip(1 - _nx ** 2 - _ny ** 2, 0, 1))
_L = np.array([-0.35, -0.7, 0.62])
_L /= np.linalg.norm(_L)
_diff = np.clip(_nx * _L[0] + _ny * _L[1] + _nz * _L[2], 0, 1)
SKULL_LEVEL = 0.1 + 0.7 * _diff + 0.3 * np.clip(2 * _diff * _nz - _L[2], 0, 1) ** 10
SKULL_LEVEL += 0.06 * (((XX * 3 + YY) % 4) == 0)              # brushed-metal grain

_sock = np.hypot(U - 5.4, YY - 26.0)
SOCKET = _sock <= 3.7
SOCKET_LIP = dilate(SOCKET) & ~SOCKET
PUPIL = _sock <= 1.6
NOSE = (YY >= 31) & (YY <= 35) & (U <= 2.0 - (YY - 31) * 0.45)
CHEEK = SKULL & (np.abs(YY - (31.5 + (U - 4) * 0.4)) < 0.5) & (U > 4) & (U < 11)
MOUTH = (YY >= 38) & (YY <= 43) & (U <= 6.5)
TEETH_GAP = MOUTH & ((XX.astype(int) % 2 == 0) | (YY == 40) | (YY == 38))
RIDGE = (U < 0.8) & (YY >= 8) & (YY <= 16)
_gem = np.abs(XX - CX) + np.abs(YY - 19) * 0.8
GEM = _gem <= 1.6
GEM_RIM = (_gem <= 2.6) & ~GEM

# nemes headdress: flares from the temples to the shoulders, horizontal channels
_nem_hw = 12.5 + np.clip(YY - 10, 0, None) * 0.42
NEMES = (YY >= 10) & (YY <= 54) & (U <= _nem_hw) & ~SKULL
NEMES_CHANNEL = NEMES & (YY.astype(int) % 4 == 0)
NEMES_EDGE = edge(NEMES | SKULL) & NEMES

# collar: stacked plates fanning out, chest core
COLLAR = (YY >= 45) & (U <= 9 + (YY - 45) * 1.2) & ~NEMES & ~SKULL
COLLAR |= (YY >= 52) & (U <= 16 + (YY - 52) * 2.5)
_core = np.hypot(XX - CX, YY - 57)
CORE = _core <= 2.3
CORE_RIM = (_core <= 3.4) & ~CORE

# glyph rain: 3x4 glyphs falling in columns
_rng = np.random.default_rng(3_000)
GLYPHS = _rng.random((24, 4, 3)) < 0.5
_cols = np.arange(1, SIZE, 6)
_col_off = _rng.uniform(0, SIZE, len(_cols))
_col_laps = _rng.choice([1, 2], len(_cols))
_col_glyph = _rng.integers(0, 24, (len(_cols), 32))
_GLITCH = (0.33, 0.78)


def frame(i: int, n: int) -> np.ndarray:
    ph = (i % n) / n
    t = TAU * ph
    img = np.zeros((SIZE, SIZE, 3))
    img[:] = (2, 6, 4)

    # --- glyph rain on the tomb wall
    for c, x0 in enumerate(_cols):
        head = (_col_off[c] + ph * SIZE * _col_laps[c]) % SIZE
        for g in range(9):
            gy = head - g * 5
            ry = int(np.floor(gy)) % SIZE
            fade = (1 - g / 9) ** 1.5
            glyph = GLYPHS[_col_glyph[c, (g + int((_col_off[c] + ph * SIZE * _col_laps[c]) // 5)) % 32]]
            col = np.array([180, 255, 190]) if g == 0 else np.array([0, 110, 40]) * fade
            for dy in range(4):
                for dx in range(3):
                    if glyph[dy, dx]:
                        put(img, (ry + dy) % SIZE, x0 + dx, col, 0.9 if g == 0 else 0.6)

    # --- nemes headdress with energy pulses running down the channels
    img[NEMES] = ramp(GUNMETAL, 0.75 - np.abs(XX - CX) / 40 - (YY - 10) / 120)[NEMES]
    run = 0.5 + 0.5 * np.sin(YY * 0.35 - 4 * t + U * 0.15)
    img[NEMES_CHANNEL] = ramp(GREEN, 0.25 + 0.6 * run ** 3)[NEMES_CHANNEL]
    img[NEMES_EDGE] = (0, 0, 0)

    # --- collar plates and the core
    img[COLLAR] = ramp(GUNMETAL, 0.55 - (YY - 44) / 40 + 0.25 * (YY.astype(int) % 3 == 0))[COLLAR]
    img[edge(COLLAR)] = (0, 0, 0)
    beat = 0.6 + 0.4 * np.sin(3 * t) ** 2
    img[CORE_RIM] = ramp(SILVER, np.full_like(YY, 0.55))[CORE_RIM]
    img[CORE] = ramp(GREEN, 0.5 + 0.45 * beat - _core / 6)[CORE]
    glow(img, 57, CX, 4, (30, 255, 80), 0.35 * beat)

    # --- skull
    skull = ramp(SILVER, SKULL_LEVEL)
    skull += (np.clip(_ny, 0, 1) ** 2 * 0.6)[..., None] * np.array([0, 120, 40])     # green underlight
    scan_y = (ph * 1.4 - 0.2) * SIZE                                                  # energy scan, once a loop
    skull += (np.exp(-((YY - scan_y) / 1.2) ** 2))[..., None] * np.array([40, 200, 80])
    img = np.where(SKULL[..., None], skull, img)
    img[CHEEK] *= 0.55
    img[RIDGE] = ramp(SILVER, SKULL_LEVEL + 0.2)[RIDGE]
    img[NOSE] = (4, 8, 6)
    img[MOUTH] = ramp(SILVER, SKULL_LEVEL * 0.85)[MOUTH]
    img[TEETH_GAP] = (5, 10, 8)
    img[SOCKET_LIP & SKULL] *= 0.5
    img[SOCKET] = (2, 10, 4)
    eye = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(2 * t)) ** 2
    img[PUPIL] = ramp(GREEN, 0.35 + 0.6 * eye - _sock / 4)[PUPIL]
    for s in (-1, 1):
        glow(img, 26.5, CX + s * 4.8, 2.6, (40, 255, 90), 0.55 * eye)
    img[GEM_RIM] = ramp(SILVER, np.full_like(YY, 0.8))[GEM_RIM]
    img[GEM] = ramp(GREEN, 0.95 - _gem / 3)[GEM]
    glow(img, 19, CX, 2.0, (60, 255, 120), 0.3 * eye)
    img[SKULL_EDGE] = (0, 4, 2)

    # --- reanimation glitch: a few rows tear sideways, green-shifted
    for g in _GLITCH:
        if abs(ph - g) < 0.02:
            rows = [r for r in range(SIZE) if (r * 7 + int(g * 100)) % 9 < 2]
            for r in rows:
                shift = 2 if r % 2 else -3
                img[r] = np.roll(img[r], shift, axis=0) * np.array([0.4, 1.3, 0.6])

    return to_frame(img)
