"""Neon Rain: the camera follows a walker with an LED umbrella down a rain-soaked cyberpunk street.

Built for LED contrast: the sky and walls are true black (LED off), and every lit thing is a
saturated neon shape. The wet street mirrors the whole scene with a moving ripple.

    sky         fixed on screen: a holographic koi swims across once, a police drone strobes past
    far towers  1 px/frame, 30 px tile: outlined towers, blinking aviation lights
    shopfronts  2 px/frame, 60 px tile: vertical glyph sign (one tube stutters) over a glowing
                doorway, a rooftop </> sign whose tubes light up one by one, a ramen bowl
                pictogram over a noodle bar window with diners, a waving neon cat over a
                vending machine
    rain        4 px/frame streaks, behind the walker
    walker      fixed on screen, black keyline: 6-frame walk cycle, colour chase round the
                umbrella hem, a pool of umbrella light on the wet kerb
    street      reflection of everything above, rippling; rain splashes
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, stamp

N = 30
TAU = 2 * np.pi
FAR_W, MID_W = 30, 60
CURB = 44                 # street line: rows below mirror the rows above

PAL = {
    "0": (0, 0, 0),
    "b": (34, 46, 150), "B": (70, 100, 255),                       # tower and roof outlines
    "M": (255, 36, 170), "m": (120, 14, 84),                       # magenta neon lit / failing
    "C": (40, 230, 255), "c": (24, 60, 170),                       # cyan neon, noodle bar glass
    "Y": (255, 206, 40), "O": (255, 120, 20), "o": (190, 60, 10),  # yellow, door glow
    "R": (255, 36, 36), "r": (90, 8, 12), "Q": (255, 36, 36),      # blinking red / off / steady red neon
    "P": (255, 120, 220),                                          # pale pink: awning, umbrella panels
    "U": (50, 90, 255),                                            # noodle bar window
    "V": (150, 60, 240), "v": (76, 26, 128), "d": (44, 14, 80),    # walker coat lit / coat / far leg
    "W": (255, 255, 255), "G": (60, 255, 140),                     # highlights, code sign
}
CHASE = [(40, 230, 255), (255, 255, 255), (255, 206, 40)]          # umbrella hem colour chase
POOL = (120, 20, 90)                                               # umbrella light on the wet street
REFLECT = np.array([(0, 0, 0), (12, 22, 70), (26, 44, 110), (16, 70, 90), (24, 110, 120), (80, 14, 60),
                    (120, 20, 90), (110, 80, 16), (120, 56, 10), (100, 14, 16), (60, 24, 100), (110, 110, 120)], float)
# ripple: bands of 3 rows sway together; a 15-frame table so the loop closes exactly
RIPPLE = np.rint(np.sin(TAU * np.arange(15)[:, None] / 15 + np.arange(7)[None] * 1.3)).astype(int)

GLYPHS = [["M.M", "MMM", "M.M"], ["MMM", ".M.", "MMM"], ["M..", "MMM", "..M"], ["MMM", "M.M", "MMM"]]
CODE = [["..G", ".G.", "G..", ".G.", "..G"],    # the rooftop sign: </>
        ["..G", "..G", ".G.", "G..", "G.."],
        ["G..", ".G.", "..G", ".G.", "G.."]]
BOWL = [  # ramen pictogram: three stair-step steam wisps over a full bowl; two wisp poses
    [".C..C..C.", ".CC.CC.CC", "..C..C..C", ".CC.CC.CC", ".C..C..C."],
    ["..C..C..C", ".CC.CC.CC", ".C..C..C.", ".CC.CC.CC", "..C..C..C"],
]
BOWL_BASE = ["YYYYYYYYYYYYY", ".YYYYYYYYYYY.", "..YYYYYYYYY..", "....YYYYY...."]
CAT = [  # maneki-neko outline; the raised paw is drawn per frame
    ".C.....C.",
    "CCC...CCC",
    "C.CCCCC.C",
    "C.......C",
    "C.W...W.C",
    "C...Q...C",
    ".C.....C.",
    ".CCCCCCC.",
    "C.......C",
    "C.......C",
    ".CCCCCCC.",
]
PAW = [["CC", "CC", ".C"], [".CC", "CC.", "C.."]]
KOI = [  # holographic koi swimming left: pointed head, black eye, spots, forked tail (two poses)
    ["......CCCC..........", "...CCCCCCCCC.....MMM", ".CCCMMCCCCCCC...MMM.", "C0CCMMMCCCCCCCCMMM..",
     "CCCCCCCCCCMMCCCCM...", ".CCCCCCCCCMMCCC.MMM.", "...CC..CCCCC....MMMM", "....C..............."],
    ["......CCCC..........", "...CCCCCCCCC........", ".CCCMMCCCCCCC...MM..", "C0CCMMMCCCCCCCCMMMMM",
     "CCCCCCCCCCMMCCCCMMMM", ".CCCCCCCCCMMCCC.MM..", "...CC..CCCCC........", "....C..............."],
]
UMBRELLA = [  # LED umbrella: magenta/pink panels, white centre rib, E = hem colour chase
    "..........WWW..........",
    "........PPMWMPP........",
    "......MPPPMWMPPPM......",
    "....MMPPPMMWMMPPPMM....",
    "..MMMPPPPMMWMMPPPPMMM..",
    ".MMMMPPPPMMWMMPPPPMMMM.",
    "MMMMPPPPPMMWMMPPPPPMMMM",
    "EEEEEEEEEEEEEEEEEEEEEEE",
    "E....E.....E.....E....E",
]
BODY = [  # hood lit pink from above, cyan visor facing right, hand on the shaft
    ".............W.........",
    "........PPPP.W.........",
    "........vvCC.W.........",
    "........vvvv.W.........",
    ".......VVVVVVY.........",
    ".......PVVVVv..........",
    ".......PVVVVv..........",
    ".......PVVVVV..........",
    ".......PVVVVVV.........",
    ".......PVVVVVV.........",
    "........VVVVVV.........",
]
LEGS = [  # near leg V, far leg d; the second half of the cycle swaps them
    ["........dVV............", ".......dd.VV...........", ".......d...VV..........",
     "......dd....V..........", "......d.....VV........."],                               # stride
    ["........dVV............", "........d.VV...........", ".......dd..V...........",
     ".......d...V...........", "......dd...VV.........."],                               # down
    ["........dVV............", "........dVV............", "........dV.............",
     "........dV.............", "........dVV............"],                               # passing
]
WALKER_X = 15
DRONE = [".BBBBB.", "BRBBBXB", ".B...B."]


def _far() -> np.ndarray:
    c = np.full((SIZE, FAR_W), ".", "<U1")
    for x0, x1, top in ((1, 8, 8), (11, 16, 3), (19, 27, 11)):
        c[top:CURB, x0:x1 + 1] = "0"
        c[top, x0:x1 + 1] = "b"          # outlines only: the inside stays true black
        c[top:CURB, x0], c[top:CURB, x1] = "b", "b"
        for y in range(top + 3, CURB, 4):
            c[y, x0 + 2:x1 - 1:3] = "Y" if (y // 4 + x0) % 3 == 0 else "."
    c[1:3, 13] = "b"
    c[0, 13] = "R"
    c[7, 4], c[10, 23] = "R", "R"
    return c


def _mid() -> np.ndarray:
    c = np.full((SIZE, MID_W), ".", "<U1")
    for x0, x1, top in ((0, 19, 12), (22, 39, 18), (42, 59, 10)):
        c[top:CURB, x0:x1 + 1] = "0"        # solid black: hides the far towers behind
        c[top, x0:x1 + 1] = "B"
        c[top:CURB, x0], c[top:CURB, x1] = "b", "b"
    # A: vertical sign and a glowing doorway under a striped awning
    c[15, 3:10], c[38, 3:10] = "M", "M"
    c[15:39, 3], c[15:39, 9] = "M", "M"
    for n, g in enumerate(GLYPHS):
        stamp(c, g, 17 + 5 * n, 5)
    c[31, 11:19] = ["P", "M"] * 4
    c[32:CURB, 12:18] = "O"
    c[32:CURB, 12], c[32:CURB, 17] = "o", "o"
    c[38:CURB, 14:16] = "0"                 # silhouette in the doorway
    c[36:38, 14:16] = "0"
    # B: rooftop </> sign on legs; ramen pictogram over a noodle bar window with two diners
    c[8, 24:39], c[16, 24:39] = "c", "c"
    c[8:17, 24], c[8:17, 38] = "c", "c"
    c[17, 26], c[17, 36] = "c", "c"
    stamp(c, BOWL_BASE, 27, 25)
    c[34, 24:38], c[CURB - 1, 24:38] = "U", "U"
    c[34:CURB, 24], c[34:CURB, 37] = "U", "U"
    c[35:CURB - 1, 25:37] = "c"
    for hx in (27, 33):
        c[37:40, hx:hx + 2] = "0"
        c[40:CURB - 1, hx - 1:hx + 3] = "0"
    # C: waving neon cat over a vending machine
    stamp(c, CAT, 15, 46)
    c[32, 46:56], c[CURB - 1, 46:56] = "M", "M"
    c[32:CURB, 46], c[32:CURB, 55] = "M", "M"
    for y in range(34, 41, 3):
        c[y, 48:54:2] = ["Y", "G", "C"]
    c[41, 50:52] = "W"
    return c


FAR, MID = _far(), _mid()
_rng = np.random.default_rng(11)
RAIN = list(zip(_rng.integers(0, 60, 40), _rng.integers(0, SIZE, 40)))
SPLASH = list(zip(_rng.integers(47, 63, 6), _rng.integers(2, 62, 6), _rng.integers(0, 10, 6)))


def _paint(img: np.ndarray, chars: np.ndarray, i: int, phase: np.ndarray) -> None:
    for ch in np.unique(chars):
        if ch == ".":
            continue
        m = chars == ch
        if ch == "R":                                # aviation lights blink on their own beat
            on = (i + phase) % 10 < 3
            img[m & on], img[m & ~on] = PAL["R"], PAL["r"]
        elif ch == "M":                              # one glyph stutters like a failing tube
            bad = (phase >= 5) & (phase <= 7) & np.isin(i % 15, (4, 5, 11))
            img[m & bad], img[m & ~bad] = PAL["m"], PAL["M"]
        else:
            img[m] = PAL[ch]


def _mid_frame(i: int) -> np.ndarray:
    c = MID.copy()
    stamp(c, PAW[(i // 5) % 2], 22, 55)              # paw waves every 5 frames
    stamp(c, BOWL[(i // 5) % 2], 22, 27)             # steam wisps sway every 5 frames
    lit = 1 + min(2, (i % 15) // 3)                  # </> tubes light one by one, then hold
    for n, g in enumerate(CODE[:lit]):
        stamp(c, g, 10, 26 + 4 * n)
    return c


def _walker(img: np.ndarray, i: int) -> None:
    step = i % 6                                     # 6-frame cycle: stride, down, passing, x2
    legs = LEGS[step % 3]
    if step >= 3:                                    # other leg forward: swap near and far
        legs = [r.replace("V", "*").replace("d", "V").replace("*", "d") for r in legs]
    rows = UMBRELLA + BODY + legs
    top = CURB - len(rows) - (step % 3 == 2)        # bob up on the passing beat
    h, w = len(rows), len(rows[0])
    sprite = np.array([list(r) for r in rows])
    mask = sprite != "."
    ring = np.zeros((h + 2, w + 2), bool)            # 1 px black keyline separates the hero
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1)):
        ring[dy:dy + h, dx:dx + w] |= mask
    for r in range(h + 2):
        for col in range(w + 2):
            y, x = top - 1 + r, WALKER_X - 1 + col
            if not (0 <= y < CURB and 0 <= x < SIZE):
                continue
            inside = 1 <= r <= h and 1 <= col <= w and mask[r - 1, col - 1]
            if inside:
                ch = sprite[r - 1, col - 1]
                img[y, x] = CHASE[(col - i) % 3] if ch == "E" else PAL[ch]
            elif ring[r, col]:
                img[y, x] = 0


def _pool(img: np.ndarray) -> None:
    """Umbrella light on the wet kerb under the walker: a bright magenta lens fading out."""
    for y, half, col in ((CURB, 10, PAL["M"]), (CURB + 1, 8, POOL), (CURB + 2, 5, POOL)):
        img[y, WALKER_X + 11 - half:WALKER_X + 12 + half] = col


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    img = np.zeros((SIZE, SIZE, 3))
    fx = np.broadcast_to((xs + i) % FAR_W, (SIZE, SIZE))
    _paint(img, FAR[:, fx[0]], i, fx)
    kx = 64 - 3 * (i % N)                            # koi crosses the sky once per loop (off-screen at the wrap)
    for r, row in enumerate(KOI[(i // 3) % 2]):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= kx + col < SIZE:
                img[1 + r, kx + col] = PAL[ch]
    mx = np.broadcast_to((xs + 2 * i) % MID_W, (SIZE, SIZE))
    _paint(img, _mid_frame(i)[:, mx[0]], i, mx)
    dx = -10 + 3 * (i % N)                           # police drone, red/blue strobe
    for r, row in enumerate(DRONE):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= dx + col < SIZE:
                lit = {"R": PAL["R"] if i % 2 else PAL["r"], "X": PAL["B"] if i % 2 == 0 else PAL["b"]}
                img[20 + r, dx + col] = lit.get(ch, PAL["b"])
    for y0, x in RAIN:                               # rain: 4 px/frame, wraps every 60 rows
        y = (y0 + 4 * i) % 60
        for d, col in ((0, (110, 170, 255)), (1, (40, 70, 150))):
            if 0 <= y - d < CURB:
                img[y - d, x] = col
    _walker(img, i)
    img[CURB] = PAL["m"]                             # wet kerb catching the magenta glow
    # street: mirror rows above the kerb, rippling, darkened onto a small reflection palette
    for y in range(CURB + 1, SIZE):
        row = np.roll(img[2 * CURB - y], RIPPLE[i % 15, (y - CURB) // 3], axis=0) * 0.45
        d = ((row[:, None, :] - REFLECT[None]) ** 2).sum(-1)
        img[y] = REFLECT[d.argmin(1)]
    _pool(img)
    for y0, x0, ph in SPLASH:                        # rain splashes on the puddles
        t = (i + ph) % 10
        if t == 0:
            img[y0, x0] = PAL["C"]
        elif t == 1:
            for ddx in (-1, 1):
                if 0 <= x0 + ddx < SIZE:
                    img[y0, x0 + ddx] = PAL["c"]
    return np.clip(img, 0, 255).astype(np.uint8)
