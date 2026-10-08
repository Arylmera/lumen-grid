"""WAAAGH!: an Ork Boy bellows the war cry, the whole frame shaking with it.

Big green head lit from above: heavy angry brow, beady red eyes, a scar with stitches across one,
flat nose, pointed ears with a brass ring, a riveted metal plate bolted to the skull. The jaw
drops as he roars, showing jagged teeth, a red maw and two huge tusks. Goff-checked shoulder
plates. Behind him a comic-book burst of red and yellow rays turns, and the "WAAAGH!" title
jitters letter by letter.
"""
from __future__ import annotations

import numpy as np

from ..core import CX, SIZE, TAU, U, XX, YY, dilate, edge, glow, put, ramp, sprite, to_frame

SKIN = [(8, 22, 4), (30, 70, 12), (60, 120, 20), (100, 165, 35), (165, 210, 80), (225, 245, 160)]
IVORY = [(70, 55, 30), (160, 140, 95), (225, 210, 165), (255, 250, 225)]
STEEL = [(20, 20, 24), (60, 58, 60), (110, 105, 100), (170, 165, 155)]

# ------------------------------------------------------------------ head geometry (jaw closed)
_cran = ((U / 13.2) ** 2 + ((YY - 28) / 11.5) ** 2 <= 1) & (YY <= 34)
_hw = np.where(YY <= 44, 13.8 + (YY - 30) * 0.36, 18.8 - (YY - 44) * 1.6)
_jaw = (YY >= 30) & (YY <= 50) & (U <= _hw)
HEAD = _cran | _jaw
MOUTH_Y = 41                       # rows >= MOUTH_Y belong to the lower jaw and drop when he roars
MOUTH_HW = 10.5

_ear = (U >= 12) & (U <= 21) & (YY >= 21) & (YY <= 31) & (YY >= 21 + (U - 12) * 0.2) \
    & (YY <= 31 - (U - 12) * 0.95)
EAR = _ear & ~HEAD

_nx = (XX - CX) / 20
_ny = (YY - 34) / 22
_nz = np.sqrt(np.clip(1 - _nx ** 2 - _ny ** 2, 0, 1))
_L = np.array([-0.4, -0.75, 0.53])
_L /= np.linalg.norm(_L)
_diff = np.clip(_nx * _L[0] + _ny * _L[1] + _nz * _L[2], 0, 1)
SKIN_LEVEL = 0.12 + 0.68 * _diff + 0.25 * np.clip(2 * _diff * _nz - _L[2], 0, 1) ** 8

BROW = (np.abs(YY - (27.5 + (9 - U) * 0.4)) < 1.3) & (U < 11)
EYE = (((U - 6) / 2.4) ** 2 + ((YY - 31.2) / 1.3) ** 2 <= 1)
PUPIL = (np.abs(U - 5.5) < 0.6) & (np.abs(YY - 31) < 0.6)
NOSE = (YY >= 34) & (YY <= 37) & (U <= 4 - (YY - 34) * 0.2)
NOSTRIL = (YY == 37) & ((np.abs(U - 2) < 0.6))
SCAR = (np.abs((XX - 38) - (YY - 24) * 0.55) < 0.6) & (YY >= 25) & (YY <= 37) & (XX > 36)
STITCH = SCAR & (YY.astype(int) % 3 == 0)
PLATE = (XX >= 19) & (XX <= 28) & (YY >= 17) & (YY <= 22) & _cran
RIVETS = PLATE & (((XX == 20) | (XX == 27)) & ((YY == 18) | (YY == 21)))
EARRING = np.abs(np.hypot(XX - 17, YY - 31) - 1.5) < 0.6

# teeth along the top of the mouth (pointing down), and the two tusks on the lower jaw
UPPER_TEETH = sprite([
    "#.#.##.#.#",
    "#...#...#.",
], top=MOUTH_Y, left=22, mirror=True)["#"]
TUSK = sprite([
    "#..",
    "##.",
    "##.",
    "###",
    "###",
    ".##",
], top=0, left=22, mirror=True)["#"]       # positioned per frame (rides the lower jaw)

# shoulders: two spiked plates with a Goff black-and-white check band
_pad = [np.hypot((XX - (CX + s * 24)) / 17, (YY - 65) / 15) for s in (-1, 1)]
PAD = [(d <= 1) for d in _pad]
CHECK = [(d <= 0.82) & (d > 0.6) for d in _pad]
SPIKES = sprite([
    "......#......#..",
    ".....###....###.",
    ".....###....###.",
    ".....###....###.",
], top=47, left=0)["#"]
SPIKES = SPIKES | SPIKES[:, ::-1]

# ------------------------------------------------------------------ the title
FONT = {
    "W": ["#....#", "#....#", "#....#", "#.##.#", "#.##.#", "##..##", "#....#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
}
TITLE = "WAAAGH!"


def _letter(ch: str, top: int, left: int) -> np.ndarray:
    m = sprite(FONT[ch], top, left)["#"]
    if ch == "W":                             # drawn 6 wide already; bolding would fill it in
        return m
    return m | np.roll(m, 1, axis=1)          # bold: thicken every stroke one pixel right


_ray_ang = np.arctan2(YY - 34, XX - CX)


def frame(i: int, n: int) -> np.ndarray:
    ph = (i % n) / n
    t = TAU * ph
    roar = np.clip(np.sin(2 * t) * 1.4, 0, 1)                  # two roars per loop
    drop = int(round(roar * 5))
    shake = (int(round(np.sin(17 * t))) if roar > 0.5 else 0)  # head judders while roaring

    # --- comic burst, rotating one ray-pair per loop so it repeats seamlessly
    rays = (np.floor((_ray_ang + t / 8) / (TAU / 16)) % 2).astype(bool)
    r = np.hypot(XX - CX, YY - 34)
    img = np.where(rays[..., None], np.array([200, 30, 15.0]), np.array([255, 140, 20.0]))
    img = img * (np.clip(1.25 - r / 50, 0.35, 1) * (0.85 + 0.15 * roar))[..., None]

    # --- shoulders
    for s in range(2):
        img[PAD[s]] = ramp(STEEL, 0.75 - (YY - 52) / 20)[PAD[s]]
        chk = CHECK[s] & PAD[s]
        board = ((XX.astype(int) // 2 + YY.astype(int) // 2) % 2 == 0)
        img[chk & board] = (240, 240, 230)
        img[chk & ~board] = (15, 15, 15)
        img[edge(PAD[s])] = (10, 8, 6)
    img[SPIKES] = ramp(STEEL, 0.95 - (YY - 47) / 7)[SPIKES]
    img[edge(SPIKES)] = (10, 8, 6)

    # --- head: upper part stays, lower jaw drops by `drop` rows
    upper = HEAD & (YY < MOUTH_Y)
    lower = np.roll(HEAD & (YY >= MOUTH_Y), drop, axis=0)
    lvl_low = np.roll(SKIN_LEVEL, drop, axis=0)
    maw = (YY >= MOUTH_Y) & (YY < MOUTH_Y + drop + 1) & (U <= MOUTH_HW - (YY - MOUTH_Y) * 0.3)
    head = upper | lower | maw
    skin = np.where(lower[..., None], ramp(SKIN, lvl_low), ramp(SKIN, SKIN_LEVEL))
    canvas = img.copy()
    canvas[EAR] = ramp(SKIN, SKIN_LEVEL * 0.9)[EAR]
    canvas[edge(EAR | head) & EAR] = (5, 12, 2)
    # cheeks stretch to bridge the gap when the jaw drops
    stretch = (YY >= MOUTH_Y) & (YY < MOUTH_Y + drop) & (U <= 13.8 + (MOUTH_Y - 30) * 0.36) & ~maw
    canvas[stretch] = ramp(SKIN, SKIN_LEVEL * 0.7)[stretch]
    head = head | stretch
    canvas = np.where((upper | lower)[..., None], skin, canvas)
    canvas[maw] = (70, 5, 8)
    tongue = maw & (YY >= MOUTH_Y + drop - 1) & (U < 5)
    canvas[tongue] = (190, 50, 60)
    canvas[UPPER_TEETH & maw] = ramp(IVORY, np.full_like(YY, 0.8))[UPPER_TEETH & maw]
    canvas[edge(head)] = (5, 12, 2)
    # face details
    canvas[BROW] = ramp(SKIN, SKIN_LEVEL * 0.45)[BROW]
    canvas[EYE] = (255, 40, 20)
    canvas[PUPIL] = (40, 0, 0)
    canvas[NOSE] = ramp(SKIN, SKIN_LEVEL * 0.8)[NOSE]
    canvas[NOSTRIL] = (5, 12, 2)
    canvas[SCAR] = (180, 120, 110)
    canvas[STITCH] = (40, 25, 20)
    canvas[PLATE] = ramp(STEEL, 0.9 - (YY - 17) / 8)[PLATE]
    canvas[edge(PLATE)] = (25, 22, 20)
    canvas[RIVETS] = (230, 225, 210)
    canvas[EARRING & ~head] = (240, 190, 60)
    canvas[EARRING & ~head & (YY < 30.5)] = (150, 100, 20)
    # tusks ride the lower jaw
    tusk = np.roll(TUSK, MOUTH_Y + drop - 5, axis=0)
    canvas[tusk] = ramp(IVORY, 0.9 - (YY - (MOUTH_Y + drop - 4)) / 10)[tusk]
    canvas[edge(tusk) & ~tusk] = (5, 12, 2)
    canvas[dilate(tusk) & ~tusk & ~head] = (5, 12, 2)
    for s in (-1, 1):
        glow(canvas, 31.2, CX + s * 6, 1.8, (255, 40, 10), 0.4)

    img = np.roll(canvas, shake, axis=1) if shake else canvas

    # --- the war cry: letters jitter, flare white-hot on each roar
    x = 10
    for k, ch in enumerate(TITLE):
        w = 6 if ch != "!" else 2
        dy = int(round(np.sin(6 * t + k * 1.3) * (0.6 + 0.6 * roar)))
        m = _letter(ch, 3 + dy, x)
        img[dilate(m) & ~m] = (60, 0, 0)
        img[m] = np.array([255, 230, 60]) * (1 - roar * 0.3) + np.array([255, 255, 255]) * roar * 0.3
        x += w + 1
    return to_frame(img)
