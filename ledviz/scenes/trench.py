"""Imperial Guard trench at night: the camera tracks along the firing line in the rain.

    sky + ruins   fixed on screen: stars, a sweeping searchlight, artillery behind a ruined
                  cathedral, an illumination flare drifting down, enemy tracers from the ruins
    no-man's land 1 px/frame, 30 px tile: mud, craters, barbed wire, a dead tree
    trench        2 px/frame, 60 px tile: sandbags, a Guardsman firing las-bolts, a Guardsman
                  smoking a lho-stick, a commissar watching, a lamp on a timber post
    rain          screen space, over everything
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, stamp

N = 30
TAU = 2 * np.pi
MID_W, FG_W = 30, 60

PAL = {
    "0": (0, 0, 0),
    "a": (18, 18, 30), "A": (32, 32, 50),                        # ruins
    "m": (24, 19, 14), "M": (34, 28, 20), "n": (60, 50, 36),     # mud, flare-lit crest
    "p": (44, 34, 24), "x": (84, 84, 92),                        # posts, wire
    "s": (54, 47, 32), "S": (88, 78, 52), "d": (28, 24, 16),     # sandbags
    "w": (40, 28, 17), "W": (66, 47, 27),                        # timber
    "h": (44, 52, 32), "H": (80, 90, 56),                        # helmet
    "c": (38, 42, 28), "C": (60, 66, 42),                        # greatcoat
    "k": (118, 88, 68), "g": (30, 28, 26), "G": (72, 70, 68),     # face, lasgun
    "q": (18, 16, 22), "Q": (70, 66, 82), "r": (150, 22, 22), "j": (206, 164, 62),  # commissar
    "u": (22, 26, 40),                                           # puddle
}
FIRE = [(110, 34, 8), (200, 80, 16), (255, 170, 60)]
FLICKER = [2, 1, 2, 1, 0, 1, 2, 2, 1, 1]       # period 10

# --------------------------------------------------------------------------- pixel maps
GUARD_FIRING = [  # leans on the parapet, lasgun to the cheek, aiming right
    "...HHHH.....",
    "..HhhhhH....",
    ".hhhhhhhh...",
    "...kkk0.....",
    "..ckkkGGGGGG",
    ".cCcgGg.....",
    "ccCccc......",
    "cccccc......",
    "cccccc......",
]
MUZZLE = (37 + 4, 10 + 11)  # tile (y, x) of the barrel tip
GUARD_SMOKING = [  # stands in the trench, lho-stick ember at the mouth
    "..HHH..",
    ".HhhhH.",
    "hhhhhhh",
    "..kkk..",
    "..kkkk.",
    ".cCcc..",
    "cCgccc.",
    "cCcgcc.",
    "cCccgc.",
    "cCcccg.",
    "cCcccc.",
    ".cc.cc.",
    ".cc.cc.",
    ".gg.gg.",
]
EMBER = (45 + 4, 31 + 5)
COMMISSAR = [  # peaked cap, long black coat with red lining, watching the line
    "..QQQQ...",
    ".QqqjqQ..",
    ".qrrrrq..",
    "QqqqqqqQ.",
    "..kkkq...",
    "..kk0k...",
    "...kk....",
    "..qrq....",
    ".Qqqqqq..",
    "Qqqjqqqq.",
    "Qqqqqqqq.",
    "Qqqqqqqqq",
    "qqqqqqqrq",
    "qqqqqqqrq",
    "qqqq.qqrq",
    "qqq..qqr.",
    ".qq..qq..",
    ".qq..qq..",
    ".gg..gg..",
]
TREE = [
    "..p...p",
    "...p.p.",
    "p...pp.",
    ".p..p..",
    "..ppp..",
    "...p...",
    "...p...",
    "...p...",
    "..ppp..",
]


def _ruins() -> np.ndarray:
    """Far skyline (fixed): broken hab blocks, a shattered tower, and a cathedral with a spire."""
    c = np.full((SIZE, SIZE), ".", "<U1")
    for x0, x1, top in ((1, 9, 24), (10, 12, 19), (13, 22, 29), (24, 31, 26), (33, 36, 22),
                        (38, 57, 25), (40, 42, 19), (52, 54, 19), (45, 49, 16), (58, 63, 27)):
        c[top:34, x0:x1 + 1] = "a"
    for x, top in ((2, 22), (4, 23), (7, 21), (11, 17), (34, 20), (41, 17), (53, 17), (47, 10)):
        c[top:34, x] = "a"   # jagged broken tops and the spire tips
    c[12:16, 46], c[12:16, 48] = "a", "a"
    for x, top in ((1, 24), (10, 19), (24, 26), (33, 22), (38, 25), (40, 19), (45, 16), (58, 27)):
        c[top:34, x] = "A"   # edge catching the flare light
    for y, x in ((27, 4), (29, 27), (28, 50), (30, 55), (25, 35)):
        c[y, x] = "f"        # fires burning in the ruins
    return c


def _no_mans_land() -> np.ndarray:
    c = np.full((SIZE, MID_W), ".", "<U1")
    for x in range(MID_W):  # ground line with a crater dip
        crest = 37 + (2 if 4 <= x <= 11 else 0) - (1 if x in (3, 12) else 0)
        c[crest, x] = "n"
        c[crest + 1:47, x] = "m"
    c[41::3, 1::5] = "M"
    c[33:38, 17] = "p"
    for x in range(13, 30):  # barbed wire coils
        c[34 + (x % 3 == 0) - (x % 3 == 2), x] = "x"
    stamp(c, TREE, 28, 21)
    return c


def _trench() -> np.ndarray:
    c = np.full((SIZE, FG_W), ".", "<U1")
    c[52:60] = "w"  # timber revetment, posts every 15 px
    c[54::3, :] = "d"
    for x in (6, 21, 36, 51):
        c[48:60, x:x + 2] = "W"
    c[60:] = "0"
    c[60:, 1::4] = "W"
    c[62, 8:20], c[62, 40:47] = "u", "u"  # puddles on the duckboards
    stamp(c, GUARD_FIRING, 37, 10)
    for row, y in enumerate((43, 46, 49)):  # staggered courses of rounded sandbags, top course lit
        for x0 in range(-(row % 2) * 3, FG_W, 6):
            for dx, (top, mid) in enumerate(zip("dSSSSd" if row == 0 else "dssssd", "ssssss")):
                c[y, (x0 + dx) % FG_W], c[y + 1, (x0 + dx) % FG_W] = top, mid
                c[y + 2, (x0 + dx) % FG_W] = "d"
    stamp(c, GUARD_SMOKING, 45, 31)
    stamp(c, COMMISSAR, 41, 46)
    c[50:53, 22] = "g"  # lamp on the post
    c[53, 21:24] = "L"
    return c


RUINS, MUD, TRENCH = _ruins(), _no_mans_land(), _trench()
_rng = np.random.default_rng(7)
STARS = list(zip(_rng.integers(0, 20, 22), _rng.integers(0, SIZE, 22)))
RAIN = list(zip(_rng.integers(0, 60, 34), _rng.integers(0, SIZE, 34)))


def _paint(img: np.ndarray, chars: np.ndarray, i: int, phase: np.ndarray) -> None:
    """Char map -> RGB over img. 'f' fires and 'L' lamps flicker; '.' is transparent."""
    for ch in np.unique(chars):
        m = chars == ch
        if ch == ".":
            continue
        if ch in "fL":
            lvl = np.array(FLICKER)[(i + 3 * phase) % 10]
            img[m] = np.array(FIRE, float)[np.maximum(lvl, 1) if ch == "L" else lvl][m]
        else:
            img[m] = PAL[ch]


def _sky(i: int) -> np.ndarray:
    v = np.zeros((SIZE, SIZE, 3))
    v[18:26] = (6, 6, 12)
    v[26:34] = (14, 10, 20)
    for k, (y, x) in enumerate(STARS):
        v[y, x] = (150, 156, 190) if k % 6 == 0 else (36, 40, 66)
    # searchlight from our lines, sweeping
    ang = 0.42 + 0.22 * np.sin(TAU * i / N)
    for t in range(4, 44):
        y, x = round(34 - t * np.cos(ang)), round(4 + t * np.sin(ang))
        if 0 <= y < SIZE:
            for dx in (0, 1):
                if x + dx < SIZE:
                    v[y, x + dx] = (52, 58, 72) if t < 16 else (36, 40, 52) if t < 30 else (24, 27, 36)
    # artillery behind the cathedral
    for f0, col in ((5, (170, 80, 22)), (6, (70, 32, 10)), (19, (170, 80, 22)), (20, (70, 32, 10))):
        if i == f0:
            v[27:34, 41:57] = col
            v[25:27, 44:54] = np.array(col) // 2
    # illumination flare: drifts down over its own 30-frame life, dimmer at both ends so the reset is invisible
    t = i % N
    fy, fx = 3 + t * 12 // N, 24
    if 3 <= t < N - 3:
        for (dy, dx), col in (((0, 0), (255, 250, 210)), ((0, 1), (150, 120, 50)), ((0, -1), (150, 120, 50)),
                              ((1, 0), (150, 120, 50)), ((-1, 0), (150, 120, 50)), ((-2, 0), (40, 40, 46)),
                              ((-3, 0), (30, 30, 36)), ((1, 1), (50, 40, 18)), ((1, -1), (50, 40, 18))):
            v[fy + dy, fx + dx] = col
    else:
        v[fy, fx] = (150, 120, 50) if t in (2, N - 3) else (50, 40, 18)
    return v


def _bolts(img: np.ndarray, i: int) -> None:
    """Our las-bolts streak right from the firing Guardsman; green tracers answer from the ruins."""
    my, mx = MUZZLE
    for f in (2, 9, 17, 23):
        a = (i - f) % N
        if a >= 6:
            continue
        sx = (mx - 2 * f) % FG_W - 2 * a          # the muzzle rides the trench layer
        for x0 in (sx, sx + FG_W):
            if a == 0:
                for dy, dx in ((0, 1), (-1, 1), (1, 1), (0, 2)):
                    if 0 <= x0 + dx < SIZE:
                        img[my + dy, x0 + dx] = (255, 140, 70)
            hx, hy = x0 + 3 + 7 * a, my - a // 2
            for d, col in ((0, (255, 200, 160)), (1, (255, 70, 40)), (2, (150, 24, 12))):
                if 0 <= hx - d < SIZE:
                    img[hy, hx - d] = col
    for f in (6, 21):
        a = (i - f) % N
        if a < 8:
            hx, hy = 58 - 6 * a, 30 + a
            for d, col in ((0, (110, 255, 130)), (1, (40, 140, 60))):
                if 0 <= hx + d < SIZE:
                    img[hy, hx + d] = col


def _smoke(img: np.ndarray, i: int, ex: int) -> None:
    """Lho-stick smoke: puffs rise 1 px every 2 frames from the ember, drifting left."""
    ey, _ = EMBER
    for k in range(3):
        age = (i - 10 * k) % N
        y, x = ey - 1 - age // 2, ex - age // 6 + (k % 2)
        if 0 <= x < SIZE and age < 24:
            img[y, x] = (80, 78, 84) if age < 8 else (48, 46, 52) if age < 16 else (28, 27, 32)


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    img = _sky(i)
    _paint(img, RUINS, i, np.broadcast_to(xs, (SIZE, SIZE)))
    mx = np.broadcast_to((xs + i) % MID_W, (SIZE, SIZE))
    _paint(img, MUD[:, mx[0]], i, mx)
    fx = np.broadcast_to((xs + 2 * i) % FG_W, (SIZE, SIZE))
    _paint(img, TRENCH[:, fx[0]], i, fx)
    ey, etx = EMBER
    for sx in ((etx - 2 * i) % FG_W, (etx - 2 * i) % FG_W + FG_W):
        if sx < SIZE:
            img[ey, sx] = (255, 150, 50) if (i % 10) < 6 else (150, 50, 14)  # ember glows on each drag
            _smoke(img, i, sx)
    _bolts(img, i)
    for y0, x in RAIN:  # 4 px/frame, wraps every 60 rows: 120 px per loop = 2 laps
        y = (y0 + 4 * i) % 60
        for d, col in ((0, (78, 88, 112)), (1, (40, 46, 62))):
            if 0 <= y - d < SIZE:
                img[y - d, x] = col
    return np.clip(img, 0, 255).astype(np.uint8)
