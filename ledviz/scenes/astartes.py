"""ASTARTES: an Ultramarine in Mk VII power armour, the hive city burning behind him.

Helmet: shaded ultramarine-blue dome, angled red eye lenses that pulse and flare, nose ridge,
mouth grille, twin cheek breathers, a gold aquila on the brow. Gorget cables, two pauldrons with
gold rims: the inverted-omega chapter badge on one, a purity seal on the other.
World: smoke-red sky, ruined gothic spires with flickering windows, artillery flashes on the
horizon, embers rising, firelight licking the armour's right edge.
"""
from __future__ import annotations

import numpy as np

from ..core import CX, SIZE, TAU, U, XX, YY, dilate, edge, glow, periodic_particles, put, ramp, sprite, to_frame

BLUE = [(4, 6, 22), (14, 28, 80), (28, 60, 150), (55, 105, 210), (140, 185, 250), (230, 240, 255)]
GOLD = [(50, 25, 5), (130, 75, 15), (205, 145, 35), (250, 205, 80), (255, 245, 190)]
LENS = [(60, 0, 0), (170, 10, 10), (255, 50, 30), (255, 170, 120), (255, 245, 230)]

# ------------------------------------------------------------------ helmet geometry
_dome = ((U / 15.5) ** 2 + ((YY - 22) / 15.5) ** 2 <= 1) & (YY <= 30)
_hw = 14.8 - np.clip(YY - 30, 0, None) * 0.26                 # faceplate narrows toward the chin
_face = (YY >= 21) & (YY <= 47) & (U <= _hw) & ~((YY >= 44) & (U > _hw - (YY - 43) * 1.6))
HELM = _dome | _face

# pseudo-normal from an ellipsoid wrapped around the whole head, light from top-left
_nx = (XX - CX) / 17
_ny = (YY - 29) / 26
_nz = np.sqrt(np.clip(1 - _nx ** 2 - _ny ** 2, 0, 1))
_L = np.array([-0.5, -0.62, 0.6])
_L /= np.linalg.norm(_L)
_diff = np.clip(_nx * _L[0] + _ny * _L[1] + _nz * _L[2], 0, 1)
_refl = 2 * _diff * _nz - _L[2]
HELM_LEVEL = 0.12 + 0.62 * _diff + 0.35 * np.clip(_refl, 0, 1) ** 12

# eye lenses: ovals with an angry inward slant cut along the top
LENS_M = (((U - 7.2) / 4.0) ** 2 + ((YY - 28) / 2.7) ** 2 <= 1) & (YY >= 25.6 + (9.5 - U) * 0.32)
BROW = dilate(dilate(LENS_M)) & ~LENS_M & (YY <= 28) & HELM
LENS_RIM = dilate(LENS_M) & ~LENS_M & ~BROW & HELM

NOSE = (U < 1.6) & (YY >= 23) & (YY <= 35)
NOSE_SIDE = (U >= 1.6) & (U < 2.6) & (YY >= 25) & (YY <= 35)

GRILLE = (YY >= 36) & (YY <= 44) & (U <= 5.8 - (YY - 36) * 0.3)
GRILLE_BAR = GRILLE & (XX % 2 == 0) & (YY > 36) & (YY < 44)

_br = np.hypot(U - 10.0, YY - 38.0)
BREATHER = _br <= 3.0
BREATHER_RIM = BREATHER & (_br > 2.1)
BREATHER_HOLE = BREATHER & ~BREATHER_RIM & ((XX + YY) % 2 == 0)

# panel seams: lens corner down the cheek to the jaw
SEAM = HELM & (np.abs(U - (11.8 - (YY - 31) * 0.12)) < 0.5) & (YY >= 31) & (YY <= 44)
SEAM |= HELM & (YY == 21) & (U < 11) & (U > 3)                # brow band line

AQUILA = sprite([
    "#.....",
    "##....",
    ".##..#",
    "..####",
    "...###",
    ".....#",
], top=13, left=26, mirror=True)["#"]

HELM_EDGE = edge(HELM)

# ------------------------------------------------------------------ armour below the helmet
GORGET = (YY >= 46) & (YY <= 55) & (U <= 12.5 - (55 - YY) * 0.25) & ~HELM
_pd = [np.hypot((XX - (CX + s * 27)) / 19, (YY - 66) / 19) for s in (-1, 1)]
PAULDRON = [(d <= 1) for d in _pd]
PAUL_RIM = [(d <= 1) & (d > 0.86) for d in _pd]
PAUL_TRIM = [(d <= 0.74) & (d > 0.68) for d in _pd]

OMEGA = sprite([
    "###...###",
    ".##...##.",
    "##.....##",
    "##.....##",
    ".##...##.",
    "..#####..",
], top=53, left=5)["#"]
OMEGA_EDGE = dilate(OMEGA) & ~OMEGA

# ------------------------------------------------------------------ the burning city
HORIZON = 50
_rng = np.random.default_rng(40_000)
_sky_h = np.zeros(SIZE)
_windows = np.zeros((SIZE, SIZE), bool)
x = 0
while x < SIZE:
    w = int(_rng.integers(3, 8))
    h = int(_rng.integers(6, 24))
    spire = _rng.random() < 0.5
    for k in range(w):
        if x + k < SIZE:
            peak = h + (int((w / 2 - abs(k - (w - 1) / 2)) * 2.2) if spire else 0)
            _sky_h[x + k] = peak
    for _ in range(int(_rng.integers(1, 4))):
        wy = HORIZON - int(_rng.integers(2, max(3, h - 1)))
        wx = x + int(_rng.integers(1, max(2, w - 1)))
        if wx < SIZE:
            _windows[wy, wx] = True
    x += w + int(_rng.integers(0, 2))
SKYLINE = YY >= HORIZON - _sky_h[None, :]
SKY = ramp([(25, 4, 4), (70, 12, 6), (150, 40, 10), (230, 110, 30)], np.clip((YY - 4) / (HORIZON - 4), 0, 1) ** 1.6)
_win_phase = _rng.uniform(0, TAU, (SIZE, SIZE))

_ex, _ey, _elap, _eph = periodic_particles(7, 30)
_FLASHES = [(0.12, 9, HORIZON - 4), (0.47, 55, HORIZON - 6), (0.81, 20, HORIZON - 3)]


def frame(i: int, n: int) -> np.ndarray:
    ph = (i % n) / n
    t = TAU * ph
    flick = 0.75 + 0.25 * np.sin(5 * t) * np.sin(3 * t + 1)

    # --- sky, smoke bands drifting left one full width per loop
    img = SKY * (0.9 + 0.1 * flick)
    smoke = 0.5 + 0.5 * np.sin((XX + ph * SIZE) * TAU / SIZE * 2 + YY * 0.45) * np.sin(YY * 0.9)
    img = img * (1 - 0.35 * (smoke * (YY < HORIZON - 4))[..., None])
    for (when, fx, fy) in _FLASHES:
        a = np.exp(-(((ph - when + 0.5) % 1 - 0.5) / 0.02) ** 2)
        glow(img, fy, fx, 5, (255, 220, 160), 0.9 * a)
    glow(img, HORIZON, CX, 22, (255, 90, 20), 0.25 * flick)

    # --- ruined spires, lit windows
    img[SKYLINE] = (8, 4, 6)
    wl = 0.5 + 0.5 * np.sin(t * 3 + _win_phase)
    img[_windows] = (np.array([255, 150, 40]) * wl[_windows][:, None])
    img[YY >= HORIZON + 4] = (12, 6, 6)

    # --- embers
    for k in range(len(_ex)):
        y = (_ey[k] - ph * SIZE * _elap[k]) % SIZE
        x = _ex[k] + 1.3 * np.sin(2 * t * _elap[k] + _eph[k])
        put(img, y, x, (255, 140 + 90 * (y / SIZE), 40), 0.9 * np.clip(y / SIZE, 0.2, 1))

    # --- pauldrons and gorget
    for s, pm in enumerate(PAULDRON):
        lv = 0.55 - (YY - 50) / 40 + (0.12 if s == 0 else 0)
        img[pm] = ramp(BLUE, lv)[pm]
        img[PAUL_RIM[s]] = ramp(GOLD, 0.75 - (YY - 48) / 30)[PAUL_RIM[s]]
        img[PAUL_TRIM[s]] = ramp(BLUE, np.full_like(YY, 0.2))[PAUL_TRIM[s]]
        img[edge(pm) & (YY < 63)] = (5, 5, 10)
    img[OMEGA_EDGE] = (10, 14, 40)
    img[OMEGA] = (235, 240, 250)
    # purity seal on the right pauldron
    sx, sy = 52, 52
    seal = np.hypot(XX - sx, YY - sy) <= 2.4
    img[dilate(seal) & ~seal] = (30, 5, 5)
    img[seal] = (175, 20, 25)
    put(img, sy - 1, sx - 1, (240, 100, 90))
    for k, x0 in enumerate((sx - 1, sx + 1)):
        for y in range(sy + 3, SIZE):
            bend = int(round(np.sin(t + k) * 1.2 * ((y - sy - 3) / 8) ** 2))
            put(img, y, x0 + bend, (225, 205, 150) if y % 2 else (150, 120, 80))
    # gorget: ribbed cable bundle
    rib = (YY.astype(int) % 2 == 0)
    img[GORGET] = np.where(rib[GORGET][:, None], [[45, 45, 55]], [[22, 22, 30]])
    img[GORGET & (U < 2)] = (70, 70, 85)

    # --- helmet
    rim = np.clip(_nx * 1.6 - 0.6, 0, 1) * flick                 # firelight from the right
    helm = ramp(BLUE, HELM_LEVEL) + (rim ** 2)[..., None] * np.array([200, 80, 20])
    # glint sweeping across the dome once per loop
    d = (XX * 0.8 + YY) / 100 - (ph * 2.2 - 0.4)
    helm += (np.exp(-(d / 0.02) ** 2) * (_nz > 0.4))[..., None] * np.array([110, 120, 140])
    img = np.where(HELM[..., None], helm, img)
    img[SEAM] *= 0.55
    img[NOSE] = ramp(BLUE, HELM_LEVEL + 0.18)[NOSE]
    img[NOSE_SIDE] *= 0.6
    img[BROW] = ramp(BLUE, HELM_LEVEL * 0.35)[BROW]
    img[GRILLE] = (8, 10, 20)
    img[GRILLE_BAR] = ramp(BLUE, HELM_LEVEL * 0.9)[GRILLE_BAR] * 0.9
    img[BREATHER_RIM] = (30, 34, 48)
    img[BREATHER & ~BREATHER_RIM] = (70, 76, 92)
    img[BREATHER_HOLE] = (10, 10, 16)
    img[AQUILA] = ramp(GOLD, 0.85 - (YY - 13) / 12)[AQUILA]
    img[HELM_EDGE] = (3, 4, 12)

    # --- lenses: pulse, inner gradient, specular dot, bloom
    pulse = 0.65 + 0.35 * np.sin(2 * t) ** 2
    lens_lv = (0.45 + 0.4 * pulse) - (YY - 27) / 10 + (1 - np.abs(U - 7.2) / 4) * 0.15
    img[LENS_M] = ramp(LENS, lens_lv)[LENS_M]
    img[LENS_RIM] = (20, 4, 4)
    for s in (-1, 1):
        put(img, 26.6, CX + s * 6.3 - 0.5 * s, (255, 250, 240))
        glow(img, 28, CX + s * 7.2, 3.2, (255, 30, 10), 0.35 * pulse)

    return to_frame(img)
