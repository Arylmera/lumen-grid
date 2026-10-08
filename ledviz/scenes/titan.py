"""Titan: a Warlord Titan strides through a burning hive city; the camera tracks it.

Built for LED contrast: true-black sky and silhouettes, every lit thing saturated (red armour,
gold trim, fire, plasma, a magenta turbo-laser beam).

    sky         fixed on screen: true black over a low red horizon glow, rising embers
    hive        1 px/frame, 30 px tile: black towers rim-lit by fire, burning windows, fires at the base
    titan       fixed on screen: stride cycle and bob, green eye slit, pulsing plasma reactor;
                fires its turbo-laser twice per loop (the hit tower erupts) and the mega-bolter between
    rubble      2 px/frame, 60 px tile: ground debris and a burning tank wreck
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, stamp

N = 30
TAU = 2 * np.pi
HIVE_W, RUB_W = 30, 60
GROUND = 58

PAL = {
    "0": (0, 0, 0),
    "A": (196, 26, 26), "a": (104, 10, 14),                       # Legio red armour / shadow
    "g": (236, 172, 36), "G": (255, 232, 120),                    # gold trim / highlight
    "E": (70, 255, 110),                                          # eye slit
    "m": (44, 54, 110), "M": (90, 110, 200),                      # gunmetal (blue-steel)
    "e": (170, 48, 0), "w": (255, 150, 30),                       # fire rim light, lit windows
    "h": (90, 12, 0),                                             # horizon glow
}
FIRE = [(120, 12, 0), (220, 44, 0), (255, 112, 0), (255, 196, 40), (255, 250, 190)]
FLICK = [3, 2, 4, 3, 2, 1, 3, 4, 2, 3]          # period 10
PLASMA = [(40, 110, 255), (120, 190, 255), (220, 240, 255)]

TORSO = [
    "....aaaaaaaa....",
    "..aaAAAAAAAAaa..",
    ".aAAAAgggAAAAAa.",
    "aAAAAAgGgAAAAAAa",
    "aAAAAAAgAAAAAAAa",
    "aAAAAAAAAAAAAAAa",
    "aaAAAAAAAAAAAAaa",
    ".aaaaAAAAAAaaaa.",
    "...aaAAAAAAaa...",
    "....aaAAAAaa....",
    ".....aaaaaa.....",
]
HEAD = [
    "..aaaa..",
    ".aAAAAa.",
    "aAAAAAAa",
    "aAEEEEEA",
    "aAAAAAAa",
    ".aaggaa.",
]
PAULDRON = [
    "..gggggg..",
    ".gAAAAAAg.",
    "gAAAgAAAAg",
    "gAAAAAAAAg",
    ".gaaaaaag.",
]
BOLTER = [  # near arm: mega-bolter, barrels pointing right
    "aAAAa.........",
    "aAAAaMMMMMMMMm",
    "aAAAammmmmmmmM",
    "aAAAaMMMMMMMMm",
    ".aaa..........",
]
LASER = ["mmmmmmmmmmmmmMMM"]  # far arm: turbo-laser barrel, tip at the right end
BANNER = [  # hangs from the hips: skull-cog on black, gold-edged
    "gggggg",
    "g0GG0g",
    "g0GG0g",
    "g0000g",
    "g0gg0g",
    "g0000g",
    ".g00g.",
    "..gg..",
]


def _fire(img: np.ndarray, base: int, x0: int, w: int, tall: int, i: int, salt: int) -> None:
    """A flame column: per-column height flickers; colour runs hot at the base, red at the tips."""
    for c in range(w):
        x = x0 + c
        if not 0 <= x < SIZE:
            continue
        h = tall + FLICK[(i + 3 * c + salt) % 10] - 2 - abs(c - w // 2)
        for d in range(max(h, 0)):
            y = base - d
            if 0 <= y < SIZE:
                img[y, x] = FIRE[min(4, max(0, 4 - d * 5 // max(h, 1)))]


def _hive() -> np.ndarray:
    c = np.full((SIZE, HIVE_W), ".", "<U1")
    for x0, x1, top in ((0, 6, 16), (9, 13, 8), (16, 24, 20), (26, 28, 12)):
        c[top:GROUND, x0:x1 + 1] = "0"
        c[top:GROUND, x0] = "e"            # edge lit by the fires below
        c[top, x0:x1 + 1] = "e"
        for y in range(top + 3, GROUND - 6, 4):
            for x in range(x0 + 2, x1, 2):
                if (x * 3 + y) % 7 < 2:
                    c[y, x] = "w"
    c[5:8, 11] = "e"                       # broken spire
    return c


def _rubble() -> np.ndarray:
    c = np.full((SIZE, RUB_W), ".", "<U1")
    c[GROUND:] = "0"
    c[GROUND, :] = "a"
    for x0, w, h in ((4, 5, 2), (18, 3, 1), (47, 6, 3), (56, 3, 1)):
        c[GROUND - h:GROUND, x0:x0 + w] = "0"
        c[GROUND - h, x0:x0 + w] = "e"
    stamp(c, ["....mmmm....", "..mmmmmmmm..", "mMMMMMMMMMMm", ".mmmmmmmmmm."], GROUND - 4, 28)  # tank wreck
    return c


HIVE, RUBBLE = _hive(), _rubble()
_rng = np.random.default_rng(5)
EMBERS = list(zip(_rng.integers(0, 60, 22), _rng.integers(0, SIZE, 22), _rng.integers(0, 3, 22)))


def _paint(img: np.ndarray, chars: np.ndarray, i: int, phase: np.ndarray) -> None:
    for ch in np.unique(chars):
        if ch == ".":
            continue
        m = chars == ch
        if ch == "w":                              # windows flicker with the fires inside
            on = (i + phase * 7) % 10 < 7
            img[m & on], img[m & ~on] = PAL["w"], PAL["e"]
        else:
            img[m] = PAL[ch]


def _titan(img: np.ndarray, i: int) -> tuple[int, int]:
    """Draw the Titan; returns the turbo-laser tip (y, x) for the beam."""
    p = i % 10                                     # stride cycle: 3 per loop
    swing = round(3 * np.sin(TAU * p / 10))
    bob = 1 if p in (2, 3, 7, 8) else 0
    ox, oy = 18, 22 + bob
    c = np.full((SIZE, SIZE), ".", "<U1")
    stamp(c, LASER, oy + 7, ox + 12)               # far arm first, behind the torso
    stamp(c, ["aAa", "aAa", "aAa"], oy + 5, ox + 11)
    for leg, dx in ((0, -swing), (1, swing)):      # pillar legs with gold knee guards, feet planted on GROUND
        lx = ox + 3 + 8 * leg + dx
        lift = 1 if (dx > 0 and leg == 1) or (dx > 0 and leg == 0) else 0
        top = oy + 11
        for y in range(top, GROUND - lift):
            c[y, lx:lx + 3] = "a"
            c[y, lx + 1] = "A"
        k = (top + GROUND) // 2
        c[k:k + 2, lx - 1:lx + 4] = "g"
        c[GROUND - 2 - lift:GROUND - lift, lx - 2:lx + 5] = "A"
        c[GROUND - 1 - lift, lx - 2:lx + 5] = "a"
    stamp(c, TORSO, oy, ox)
    stamp(c, BANNER, oy + 10, ox + 5)
    stamp(c, HEAD, oy + 4, ox + 13)
    stamp(c, PAULDRON, oy + 1, ox + 6)
    stamp(c, BOLTER, oy + 7, ox + 9)
    _paint(img, c, i, np.zeros((SIZE, SIZE), int))
    pl = PLASMA[[0, 1, 2, 1, 0][i % 5]]            # reactor vents on the back pulse
    for y in range(oy + 2, oy + 6):
        img[y, ox - 1] = pl
    img[oy + 3, ox - 2] = PLASMA[0]
    return oy + 7, ox + 12 + len(LASER[0])


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    img = np.zeros((SIZE, SIZE, 3))
    img[44:GROUND] = PAL["h"]
    img[50:GROUND] = FIRE[0]
    hx = np.broadcast_to((xs + i) % HIVE_W, (SIZE, SIZE))
    _paint(img, HIVE[:, hx[0]], i, hx)
    for k, tx in enumerate((3, 20)):               # fires at the tower bases ride the hive layer
        for sx in ((tx - i) % HIVE_W + o for o in (-HIVE_W, 0, HIVE_W)):
            _fire(img, GROUND - 1, sx, 6, 8, i, 4 * k)
    for y0, x, k in EMBERS:                        # embers rise 2 px/frame, wrap every 60 rows
        y = 57 - (y0 + 2 * i) % 60
        if 0 <= y < SIZE:
            img[y, (x + (y0 + 2 * i) // 15) % SIZE] = FIRE[2 + k]
    tip_y, tip_x = _titan(img, i)
    for f0 in (8, 23):                             # turbo-laser: white core, magenta falloff
        a = i % N - f0
        if 0 <= a < 3:
            core, edge = [((255, 255, 255), (255, 70, 200)), ((255, 120, 220), (150, 20, 120)), ((150, 20, 120), None)][a]
            img[tip_y, tip_x:] = core
            if edge:
                img[tip_y - 1, tip_x:], img[tip_y + 1, tip_x:] = edge, edge
        b = i % N - f0 - 1                         # the struck tower erupts
        if 0 <= b < 5:
            r = [1, 2, 4, 5, 5][b]
            col = [FIRE[4], FIRE[4], FIRE[3], FIRE[2], FIRE[1]][b]
            yy, xx = np.mgrid[0:SIZE, 0:SIZE]
            blast = (yy - tip_y) ** 2 + (xx - 58) ** 2 <= r * r
            img[blast] = col
            if b >= 2:
                img[(yy - tip_y) ** 2 + (xx - 58) ** 2 <= (r - 2) ** 2] = FIRE[4]
    if 13 <= i % N <= 19 and i % 2:                # mega-bolter burst: muzzle flash + tracers
        my, mx = 22 + (1 if i % 10 in (2, 3, 7, 8) else 0) + 9, 18 + 9 + 14
        img[my - 1:my + 2, mx] = FIRE[3]
        img[my, mx + 1] = FIRE[4]
        for t in range(3):
            x = mx + 4 + 6 * t + 2 * (i % 3)
            if x + 2 < SIZE:
                img[my, x:x + 2] = FIRE[3]
    rx = np.broadcast_to((xs + 2 * i) % RUB_W, (SIZE, SIZE))
    _paint(img, RUBBLE[:, rx[0]], i, rx)
    for sx in ((34 - 2 * i) % RUB_W + o for o in (-RUB_W, 0)):  # the wreck burns
        _fire(img, GROUND - 5, sx, 5, 7, i, 2)
    return np.clip(img, 0, 255).astype(np.uint8)
