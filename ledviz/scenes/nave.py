"""Cathedral-ship nave: the camera tracks sideways down an endless nave aboard an Imperial starship.

Every layer is a hand-placed pixel map (one character per palette colour) that tiles horizontally.
The camera moves in whole-pixel steps and each layer shifts an exact number of its own tiles per
loop, so the 30-frame loop has no seam:

    void        fixed on screen (stars at infinity), seen only through the void-ports
    nave wall   1 px/frame, 30 px tile: vault ribs, stained-glass saint, void-port, skull niche, pilgrim, candles
    foreground  2 px/frame, 60 px tile: pillar, banner, censer and smoke, servo-skull
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE

N = 30            # frames per loop: the Pixoo 64 replays only the first ~30-32 frames
TAU = 2 * np.pi
WALL_W, FG_W = 30, 60

PAL = {
    "0": (0, 0, 0),
    "1": (14, 9, 16), "2": (30, 19, 28), "3": (50, 33, 42), "4": (78, 54, 58),       # stone
    "g": (84, 52, 16), "h": (150, 100, 28), "j": (215, 165, 55), "k": (255, 228, 140),  # gilt
    "c": (150, 136, 108), "d": (222, 212, 180), "b": (90, 78, 60),                      # bone
    "E": (255, 40, 30), "e": (110, 10, 10),                                               # lens
    "5": (34, 24, 32), "6": (58, 40, 46), "7": (130, 70, 36),                           # robes, candle rim
    "r": (70, 8, 14), "s": (140, 18, 24), "t": (196, 46, 38),                           # banner
    "w": (205, 192, 160), "i": (130, 170, 215),                                           # wax, port glint
}
GLASS = {  # colour-cycled stained glass: upper case = lit pane, lower case = shaded pane
    "R": [(90, 10, 22), (172, 26, 32), (240, 74, 60)],
    "U": [(14, 24, 88), (30, 62, 172), (84, 134, 240)],
    "Y": [(128, 78, 10), (212, 152, 32), (255, 222, 112)],
}
FLAME = [(160, 44, 10), (242, 124, 22), (255, 224, 128)]
FLICKER = [2, 1, 2, 2, 1, 0, 1, 2, 2, 1]   # period 10 divides N
SMOKE = [(92, 86, 96), (60, 56, 66), (34, 31, 40)]

# ------------------------------------------------------------------------------- pixel maps
LANCET = [  # stained-glass saint: gold halo, red robe, gold sword, framed by stone tracery
    ".....4.....",
    "....3Y3....",
    "...3yYy3...",
    "..3uUYUu3..",
    ".3UuyYyuU3.",
    "3uuyYYYyuu3",
    "3uUYdddYUu3",
    "3UuYdddYuU3",
    "3uUyYdYyUu3",
    "3U1RRRRR1U3",
    "3uRRrRrRRu3",
    "3URjRRRjRU3",
    "3uRRRYRRRu3",
    "3URRrYrRRU3",
    "3uRRRYRRRu3",
    "3U1RrYrR1U3",
    "3uURRYRRUu3",
    "3UuRrRrRuU3",
    "3uURRRRRUu3",
    "3u1RRRRR1u3",
    "3UuRrRrRuU3",
    "3uYyYyYyYu3",
    "3yYyYkYyYy3",
    "31111111113",
    "44444444444",
]
NICHE = [  # skull in a pier niche
    "..444..",
    ".40004.",
    "40ddd02",
    "4ddddd2",
    "4d0d0d2",
    "40ddd02",
    "40b0b02",
    "4222222",
]
PILGRIM = [  # hooded figure kneeling in prayer, rim-lit by the candles on its right
    "..55..",
    ".5567.",
    ".5567.",
    ".55567",
    "555667",
    "555567",
    "5555667",
    "1111111",
]
CANDLES = [
    "F.F.F",
    "f.f.f",
    "w.w.w",
    "w.w.w",
    "hhhhh",
    "..h..",
    "..g..",
    ".ggg.",
]
BANNER = [
    "rsssssssr",
    "rsjjjjjsr",
    "rsssssssr",
    "rsjskjssr",
    "rssjkjssr",
    "rjjjkjjjr",
    "rssjjjssr",
    "rsssjsssr",
    "rsssssssr",
    "rsttttssr",
    "rsssssssr",
    "rsssssssr",
    "rsjjjjjsr",
    "rsssssssr",
    ".rsssssr.",
    "..rsssr..",
    "...rsr...",
    "....r....",
]
CENSER = [
    "..h..",
    ".hjh.",
    "hjkjh",
    "gfffg",
    "ghhhg",
    ".ggg.",
]
SERVO = [
    "...g...",
    "..cdd..",
    ".cdddd.",
    "c0ddEdd",
    ".cdddd.",
    "..b0b..",
    ".g...g.",
]


def stamp(c: np.ndarray, rows: list[str], top: int, left: int) -> None:
    """Paint an ASCII map into a char canvas; '.' is transparent; x wraps around the tile."""
    h, w = c.shape
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch != "." and 0 <= top + r < h:
                c[top + r, (left + col) % w] = ch


def _wall() -> np.ndarray:
    c = np.full((SIZE, WALL_W), "1", "<U1")
    # stone lit by the window, falling off into dark; sparse mortar one step darker
    for y in range(12, 50):
        for x in range(WALL_W):
            lit = abs(x - 15) <= 9 and 12 <= y < 50
            joint = y % 6 == 0 or ((x + 4 * ((y // 6) % 2)) % 8 == 0 and y % 6 == 3)
            c[y, x] = ("1" if joint else "2") if lit else ("0" if joint else "1")
    # vault: dark web above two diagonal ribs meeting at a gilt boss
    c[:11] = "0"
    for x in range(WALL_W):
        yr = round(1 + 9 * (abs(x - 15) / 15) ** 1.5)
        c[yr + 1:11, x] = "1"
        c[yr, x], c[yr + 1, x] = "h", "g"
        if abs(x - 15) <= 8:  # wall arch framing the window
            c[round(5 + 6 * (abs(x - 15) / 8) ** 1.3), x] = "3"
    stamp(c, [".j.", "jkj", ".j."], 0, 14)
    # pier between windows (wraps around the tile edge) with a capital and a skull niche
    for x in (27, 28, 29, 0, 1, 2, 3):
        c[11:50, x] = "2"
    c[11:50, 27], c[11:50, 28], c[11:50, 3] = "4", "3", "1"
    for x in (26, 27, 28, 29, 0, 1, 2, 3, 4):
        c[11, x], c[12, x] = "h", "g"
    stamp(c, NICHE, 24, 27)
    stamp(c, LANCET, 9, 10)
    # void-port: riveted bronze ring, top-left lit, interior shows the void layer ('v')
    for y in range(37, 50):
        for x in range(9, 22):
            r = np.hypot(y - 43, x - 15)
            if r <= 4.6:
                c[y, x] = "v"
            elif r <= 5.7:
                c[y, x] = "j" if (y - 43) + (x - 15) < 0 else "h"
            elif r <= 6.6:
                c[y, x] = "g"
    for a in range(8):
        c[43 + round(5.1 * np.sin(a * TAU / 8)), 15 + round(5.1 * np.cos(a * TAU / 8))] = "k"
    c[40, 13], c[39, 14] = "i", "i"
    # plinth and floor
    c[50], c[51] = "4", "3"
    c[52:] = "1"
    for y, off in ((54, 0), (57, 5), (61, 2)):
        c[y] = "0"
        c[y + 1:, off::10] = "0"
    c[58:, 16:27][c[58:, 16:27] == "1"] = "2"  # candle spill on the flagstones
    stamp(c, PILGRIM, 53, 6)
    stamp(c, CANDLES, 53, 19)
    return c


def _foreground() -> np.ndarray:
    c = np.full((SIZE, FG_W), ".", "<U1")
    # pillar shaft close to the camera: near-black, fluted, warm rim light on the right edge
    shaft = "01121121120" + "7"
    for x, ch in enumerate(shaft):
        c[:, x] = ch
    c[:, 12] = "0"
    for y in (17, 46):  # gilt bands
        c[y, :12], c[y + 1, :12] = "h", "g"
        c[y, 2:11:4] = "k"
    c[59:, :13] = "1"
    c[59, :13] = "3"
    c[0, 20:33] = "g"  # banner rod
    return c


WALL, FG = _wall(), _foreground()


def _void(i: int) -> np.ndarray:
    """Space behind the ports. Stars at infinity stay fixed on screen while the camera tracks."""
    v = np.zeros((SIZE, SIZE, 3))
    rng = np.random.default_rng(40)
    for k, (y, x) in enumerate(zip(rng.integers(36, 51, 46), rng.integers(0, SIZE, 46))):
        bright = k % 5 == 0 and (i + k) % 15 not in (0, 1)
        v[y, x] = (210, 216, 255) if bright else (34, 42, 92)
    v[44:47, 4:22] += (22, 8, 34)  # faint nebula band
    # escort ship and its lance strike once per loop
    for dy, row in enumerate([".ccc..", "cdddcc", ".ccc.."]):
        for dx, ch in enumerate(row):
            if ch != ".":
                v[41 + dy, 42 + dx] = (110, 116, 132) if ch == "c" else (160, 168, 190)
    v[42, 48] = (120, 220, 255)
    age = i - 12
    if 0 <= age < 4:
        col = [(255, 255, 255), (150, 230, 255), (60, 120, 200), (22, 40, 92)][age]
        for x in range(0, 42):
            v[42 + (41 - x) // 14, x] = col
    return v


def _resolve(chars: np.ndarray, wx: np.ndarray, i: int, under: np.ndarray) -> np.ndarray:
    """Char map -> RGB. Glass and flames are coloured per frame; '.' and 'v' show `under`."""
    img = under.copy()
    yy = np.arange(SIZE)[:, None]
    for ch in np.unique(chars):
        m = chars == ch
        if ch in ".v":
            continue
        if ch.upper() in GLASS:
            shimmer = (wx + yy - 2 * i) % 30          # a band of light sweeping the panes, period 15
            lvl = int(ch.isupper()) + (shimmer < 3).astype(int) - ((shimmer >= 15) & (shimmer < 17))
            ramp = np.array(GLASS[ch.upper()], float)
            img[m] = ramp[np.clip(lvl, 0, 2)[m]]
        elif ch in "fF":
            lvl = np.array(FLICKER)[(i + 3 * wx) % 10]
            ramp = np.array(FLAME, float)
            if ch == "f":
                img[m] = ramp[lvl[m]]
            else:  # flame tip only on the tall beats
                tip = m & (lvl == 2)
                img[tip] = ramp[1]
                img[m & ~tip] = PAL["1"]
        else:
            img[m] = PAL[ch]
    return img


def _fg_frame(i: int) -> np.ndarray:
    """Foreground tile for frame i: static pillar plus the swaying banner, censer, smoke, skull."""
    c = FG.copy()
    for r, row in enumerate(BANNER):  # rows ripple, bottom moves most
        stamp(c, [row], 1 + r, 22 + round(1.3 * r / len(BANNER) * np.sin(TAU * i / N - r * 0.35)))
    swing = round(2 * np.sin(TAU * i / N))
    for y in range(0, 26):  # chain: a straight line from the hook to the swinging censer
        c[y, 48 + round(swing * y / 26)] = "g" if y % 2 == 0 else "h"
    stamp(c, CENSER, 26, 46 + swing)
    for k in range(3):  # incense puffs: rise 1 px every 2 frames, fade over a 30-frame life
        age = (i - 10 * k) % N
        y = 24 - age // 2
        x = 48 + swing + round(1.5 * np.sin(TAU * age / N + k))
        c[y, x % FG_W] = "SMO"[min(age // 10, 2)]
    bob = round(np.sin(TAU * i / 15))
    stamp(c, SERVO, 31 + bob, 33)
    if i % 15 in (7, 8):
        c[c == "E"] = "e"
    return c


_SMOKE_PAL = {"S": SMOKE[0], "M": SMOKE[1], "O": SMOKE[2]}
PAL.update(_SMOKE_PAL)


def _motes(img: np.ndarray, i: int) -> None:
    """Dust drifting down in the light below each window, wall coordinates."""
    for k, (x0, y0) in enumerate([(12, 30), (17, 33), (14, 36), (19, 28)]):
        t = (i + 8 * k) % N
        if 4 <= t < 26:
            for x in range(SIZE):
                if (x + i) % WALL_W == x0:
                    y = y0 + t // 3
                    if img[y, x].sum() < 200:
                        img[y, x] = (120, 88, 38)


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    wx = np.broadcast_to((xs + i) % WALL_W, (SIZE, SIZE))
    img = _resolve(WALL[:, wx[0]], wx, i, _void(i))
    _motes(img, i)
    fx = np.broadcast_to((xs + 2 * i) % FG_W, (SIZE, SIZE))
    img = _resolve(_fg_frame(i)[:, fx[0]], fx, i, img)
    return np.clip(img, 0, 255).astype(np.uint8)
