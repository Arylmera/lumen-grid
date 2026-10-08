"""Cyberpunk city from a maglev window: a passenger rides through the neon city at night in the rain.

    carriage    fixed on screen: window frame, the passenger's hooded silhouette (rim-lit by the
                neon outside), a route ticker scrolling amber text
    sky         fixed on screen (far): purple smog bands and an advertising blimp
    far towers  1 px/frame, 30 px tile: window grids, blinking aviation lights
    mid towers  2 px/frame, 60 px tile: vertical neon sign, a BAR sign, lit windows
    pylons      4 px/frame, 120 px tile: the track pylon whipping past
    glass       screen space: rain streaks sliding down and back, a flying car overtaking
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, stamp

N = 30
TAU = 2 * np.pi
FAR_W, MID_W, PYL_W, TICK_W = 30, 60, 120, 60

PAL = {
    "0": (0, 0, 0),
    "f": (22, 12, 38), "y": (110, 84, 34), "c": (34, 96, 120),         # far towers, windows
    "m": (10, 6, 20), "w": (150, 100, 44), "k": (36, 20, 44),          # mid towers, plates
    "P": (255, 64, 176), "p": (110, 22, 78),                           # pink neon lit / dim
    "Z": (60, 230, 255), "z": (20, 80, 100),                           # cyan neon lit / dim
    "F": (30, 28, 42), "G": (62, 58, 80), "1": (10, 8, 16),             # carriage metal, shadow
    "o": (8, 6, 14), "T": (255, 150, 30), "t": (26, 12, 4),            # silhouette, ticker
    "R": (255, 30, 30), "r": (70, 6, 6),                               # aviation light
}
RIM = [(255, 64, 176), (150, 70, 230), (60, 230, 255)]                # neon rim on the passenger

FONT = {
    "N": ["ZZ.", "Z.Z", "Z.Z", "Z.Z", "Z.Z"], "E": ["ZZZ", "Z..", "ZZ.", "Z..", "ZZZ"],
    "X": ["Z.Z", "Z.Z", ".Z.", "Z.Z", "Z.Z"], "T": ["ZZZ", ".Z.", ".Z.", ".Z.", ".Z."],
    "S": ["ZZZ", "Z..", "ZZZ", "..Z", "ZZZ"], "C": ["ZZZ", "Z..", "Z..", "Z..", "ZZZ"],
    "O": ["ZZZ", "Z.Z", "Z.Z", "Z.Z", "ZZZ"], "R": ["ZZ.", "Z.Z", "ZZ.", "Z.Z", "Z.Z"],
    "7": ["ZZZ", "..Z", ".Z.", ".Z.", ".Z."], "B": ["ZZ.", "Z.Z", "ZZ.", "Z.Z", "ZZ."],
    "A": [".Z.", "Z.Z", "ZZZ", "Z.Z", "Z.Z"], " ": ["...", "...", "...", "...", "..."],
}
GLYPHS = [["P.P", "PPP", "P.P"], ["PPP", ".P.", "PPP"], ["P..", "PPP", "..P"], ["PPP", "P.P", "PPP"],
          [".P.", "PPP", ".P."]]
CAR = [".kkkk..", "ZkGGGkT", "..k.k.."]  # cyan headlight leads, amber tail


def text(c: np.ndarray, s: str, top: int, left: int, ch: str) -> None:
    for n, letter in enumerate(s):
        stamp(c, [row.replace("Z", ch) for row in FONT[letter]], top, left + 4 * n)


def _far() -> np.ndarray:
    c = np.full((SIZE, FAR_W), ".", "<U1")
    for x0, x1, top in ((0, 6, 14), (8, 12, 20), (14, 22, 9), (24, 29, 16)):
        c[top:, x0:x1 + 1] = "f"
        for y in range(top + 2, SIZE, 3):
            for x in range(x0 + 1, x1, 2):
                if (x * 7 + y * 3) % 5 < 2:
                    c[y, x] = "y" if (x + y) % 3 else "c"
    c[5:9, 18] = "f"   # spire
    for y, x in ((13, 3), (19, 10), (4, 18), (15, 26)):
        c[y, x] = "R"
    return c


def _mid() -> np.ndarray:
    c = np.full((SIZE, MID_W), ".", "<U1")
    for x0, x1, top in ((0, 17, 17), (22, 37, 24), (42, 57, 13)):
        c[top:, x0:x1 + 1] = "m"
        for y in range(top + 3, SIZE, 4):
            for x in range(x0 + 2, x1 - 1, 3):
                if (x * 5 + y) % 7 < 3:
                    c[y, x] = "w"
    c[8:13, 50] = "k"   # antenna
    c[8, 50] = "R"
    c[19:42, 12:19] = "k"  # vertical sign plate with stacked glyphs
    for n, g in enumerate(GLYPHS):
        stamp(c, g, 20 + 4 * n, 14)
    c[26:34, 23:37] = "k"  # BAR sign
    text(c, "BAR", 27, 25, "Z")
    return c


def _carriage() -> np.ndarray:
    """Fixed foreground: window frame, wall, ticker plate, and the passenger silhouette."""
    c = np.full((SIZE, SIZE), ".", "<U1")
    c[:3], c[44:], c[:, :3], c[:, 61:] = "F", "1", "F", "F"
    c[3, 3:61], c[3:44, 3] = "G", "G"          # inner lip catching light
    c[44, 3:61], c[45, :] = "G", "F"           # sill
    for y, x in ((3, 3), (3, 60), (43, 3), (43, 60), (4, 3), (3, 4), (3, 59), (4, 60)):
        c[y, x] = "F"                          # rounded corners
    c[49:58, 29:62] = "F"
    c[50:57, 30:61] = "t"
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    hood = ((yy - 36) / 11) ** 2 + ((xx - 10) / 8) ** 2 <= 1
    shoulders = (yy >= 46) & (xx <= 12 + 1.2 * (yy - 46))
    sil = hood | shoulders
    c[sil] = "o"
    edge = sil & (~np.roll(sil, -1, axis=1) | ~np.roll(sil, 1, axis=0))
    c[edge & (xx >= 12) & (yy >= 27)] = "E"     # rim light only on the side facing the window
    c[34, 16:18] = "V"                          # visor glow at the hood opening
    return c


FAR, MID, CARRIAGE = _far(), _mid(), _carriage()
TICKER = np.full((5, TICK_W), ".", "<U1")
text(TICKER, "NEXT SECTOR 7  ", 0, 0, "T")
GLASS = np.zeros((SIZE, SIZE), bool)
GLASS[4:44, 4:60] = True
_rng = np.random.default_rng(3)
DROPS = list(zip(_rng.integers(0, 40, 16), _rng.integers(4, 76, 16)))


def _paint(img: np.ndarray, chars: np.ndarray, i: int, phase: np.ndarray, rim) -> None:
    for ch in np.unique(chars):
        if ch == ".":
            continue
        m = chars == ch
        if ch == "R":   # aviation lights blink, each on its own beat
            on = (i + phase) % 10 < 2
            img[m & on], img[m & ~on] = PAL["R"], PAL["r"]
        elif ch == "P":  # one glyph column stutters like a failing tube
            bad = (phase == 15) & np.isin(i % 15, (3, 4, 9))
            img[m & bad], img[m & ~bad] = PAL["p"], PAL["P"]
        elif ch == "E":
            img[m] = rim
        elif ch == "V":
            continue
        else:
            img[m] = PAL[ch]


def _sky(i: int) -> np.ndarray:
    v = np.zeros((SIZE, SIZE, 3))
    for y0, y1, col in ((0, 12, (16, 4, 28)), (12, 22, (34, 8, 46)), (22, 32, (58, 14, 62)), (32, 64, (74, 20, 70))):
        v[y0:y1] = col
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    blimp = ((yy - 9) / 3) ** 2 + ((xx - 44) / 9) ** 2 <= 1
    v[blimp] = (28, 18, 40)
    for x in range(39, 49):  # ad screen: colour bars scrolling 1 px per frame, period 6
        v[8:11, x] = [(255, 64, 176), (255, 210, 60), (60, 230, 255)][((x + i) % 6) // 2]
    return v


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    rim = RIM[(i // 5) % 3] if (i // 5) % 6 < 3 else RIM[2 - (i // 5) % 3]
    img = _sky(i)
    fx = np.broadcast_to((xs + i) % FAR_W, (SIZE, SIZE))
    _paint(img, FAR[:, fx[0]], i, fx, rim)
    mx = np.broadcast_to((xs + 2 * i) % MID_W, (SIZE, SIZE))
    _paint(img, MID[:, mx[0]], i, mx, rim)
    px = (xs + 4 * i) % PYL_W
    img[:, (px >= 0) & (px < 4)] = PAL["m"]          # track pylon whipping past
    img[30, (px >= 0) & (px < 4)] = PAL["P"]
    cx = 70 - 3 * i                                   # flying car overtakes once per loop
    for r, row in enumerate(CAR):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= cx + col < SIZE:
                img[18 + r, cx + col] = PAL[ch]
    for y0, x0 in DROPS:                             # rain on the glass, blown back by the speed
        t = (y0 + 4 * i) % 40
        y, x = 4 + t, (x0 - t // 2) % 72
        for d, col in ((0, (120, 120, 170)), (1, (60, 56, 96))):
            if 4 <= y - d < 44 and 4 <= x + d < 60:
                img[y - d, x + d] = col
    img[~GLASS] = 0
    _paint(img, CARRIAGE, i, fx, rim)
    tick = TICKER[:, (np.arange(30) + 2 * i) % TICK_W]
    plate = img[51:56, 30:60]
    plate[tick == "T"] = PAL["T"]
    img[CARRIAGE == "V"] = (60, 230, 255) if i % 10 < 7 else (20, 80, 100)  # visor readout pulses
    return np.clip(img, 0, 255).astype(np.uint8)
