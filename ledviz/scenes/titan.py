"""Titan: a Warlord Titan of Legio Mortis strides through a burning hive city; the camera tracks it.

Built for LED contrast: true-black sky and silhouettes, every lit thing saturated (blood-red
armour, gold trim, fire, blue plasma, a magenta turbo-laser beam).

    sky         fixed on screen: true black over a low red horizon glow, rising embers
    hive        1 px/frame, 30 px tile: gothic black towers rim-lit by fire (spire, broken arch,
                cathedral with a rose window), flickering windows, fire columns at the base
    rubble      2 px/frame, 60 px tile: ground line, debris and a burning tank wreck
    troopers    3 px/frame on screen: tiny guardsmen flee past the Titan's feet, for scale
    titan       fixed on screen, black keyline: 10-frame stride (planted foot rides the ground,
                the other lifts and swings, the body sinks on each footfall), crenellated
                carapace with spires, low brooding head with a green eye slit, pulsing plasma
                reactor, skull-cog banner; fires its turbo-laser twice per loop (the struck tower
                erupts) and the mega-bolter between the shots
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, stamp

N = 30
HIVE_W, RUB_W = 30, 60
GROUND = 58
GLOW = 44                                        # red horizon glow from here down

PAL = {
    "0": (0, 0, 0),
    "R": (255, 64, 48), "A": (204, 22, 22), "a": (112, 8, 16),    # Legio red: lit / armour / shadow
    "g": (232, 160, 24), "G": (255, 230, 110),                    # gold trim / highlight
    "E": (80, 255, 120),                                          # eye slit
    "m": (36, 52, 128), "M": (80, 116, 230), "S": (170, 205, 255),  # blue-steel guns
    "e": (170, 48, 0), "w": (255, 150, 30),                       # fire rim light, lit windows
    "h": (90, 12, 0),                                             # horizon glow
    "P": (40, 110, 255),                                          # plasma (recoloured per frame)
}
FIRE = [(120, 12, 0), (220, 44, 0), (255, 112, 0), (255, 196, 40), (255, 250, 190)]
FLICK = [3, 2, 4, 3, 2, 1, 3, 4, 2, 3]          # period 10
PLASMA = [(40, 110, 255), (120, 190, 255), (220, 240, 255)]
PULSE = [0, 1, 2, 1, 0]                          # reactor, period 5
BEAM = [(150, 20, 120), (255, 70, 200), (255, 255, 255)]
SHOTS = (3, 18)                                  # turbo-laser fires twice per loop
HIT_X, HIT_Y = 61, 31                            # lands on the spire, then on the cathedral

# Titan parts, all facing right. The body origin (OX, oy) is the carapace's top-left corner.
CARAPACE = [
    "......G.....G.....G........",
    "......g.....g.....g........",
    "......g....aga....g........",
    ".....aga...aga...aga.......",
    "..RR.RR.RR.RR.RR.RR.RR.....",
    "..RRRRRRRRRRRRRRRRRRRRR....",
    ".ggggggggggggggggggggggg...",
    ".aAAAAAAAAAAAAAAAAAAAAAAg..",
    "aAAAAAAAAAAAAAAAAAAAAAAAAg.",
    "aAAAAAAAAAAAAAAAAAAAAAAAAAg",
    "aAAgAAAAgAAAAgAAAAgAAAAAAAg",
    "aAAAAAAAAAAAAAAAAAAAAAAAAAg",
    "aAAAAAAAAAAAAAAAAAAAAAAAAAg",
    "aaAAAAAAAAAAAAAAAAAAAAAAAAg",
    ".aaaaaaaaaaaaaaaaaaaaaaaaag",
    "..gggggggggggggggggggggggg.",
]
REACTOR = [  # plasma reactor on the back: coils recoloured per frame
    "..mm",
    ".mPm",
    "mPPm",
    "mPPm",
    "mPPm",
    ".mPm",
    "..mm",
]
HEAD = [
    "..aaaaa....",
    ".aRRRRRa...",
    "aAAAAAAAa..",
    "aAAAAAAAAg.",
    "aAAAgggggGG",
    "aAAA00000..",
    "aAAA0EEEE0.",
    "aAAAAA0A0..",
    ".aAgAgAg...",
    "..aaaaa....",
]
PELVIS = [
    "..aaaaaaaaaaa..",
    ".aAAAAAAAAAAAa.",
    "aAAgggggggggAAa",
    "aAAAAAAAAAAAAAa",
    ".aaaaaaaaaaaaa.",
]
PAULDRON = [  # a domed shoulder plate over one lower lame
    "...gggggg...",
    ".ggRRRRRRgg.",
    "gRRRAAAAAAAg",
    "gRAAAAAAAAAg",
    "gAAAAAAAAAAg",
    "gaAAAAAAAAag",
    "gggggggggggg",
    ".gaAAAAAAag.",
    "..gggggggg..",
]
TROOPER = [["G.", "M.", "MM", "m."], ["G.", "M.", "M.", ".m"]]   # fleeing guardsman, 2 run poses
TROOPERS = ((0, GROUND - 4), (7, GROUND - 4), (50, GROUND - 4))   # (x0, top): run at 3 px/frame
BOLTER = [  # near arm: red forearm into a mega-bolter with three barrels
    "..aAAAa......................",
    "..aAAAa......................",
    "aaAAAAAaammmmmm..............",
    "aAgggggAamMMMMm0SSSSSSSSSSSM.",
    "aAAAAAAAamMSMMm0mmmmmmmmmmm..",
    "aAAAAAAAamMMMMm0SSSSSSSSSSSM.",
    ".aaaaaaa.mMMMMm0mmmmmmmmmmm..",
    ".........mMMMMm0SSSSSSSSSSSM.",
    ".........mmmmmm..............",
]
LASER = [  # far arm: red housing, long turbo-laser barrel with cooling rings and a lens tip
    "aAAAAAAAa...................",
    "aAAggggAammmmmmmmmmmmmmmmmm.",
    "aAAAAAAAamMMMMgMMMMgMMMMgMSS",
    "aaaaaaaaammmmmmmmmmmmmmmmmm.",
]
BANNER = [  # hangs from the hips on a gold bar: Legio red and black, gold skull-cog, swallowtail
    "ggggggggg",
    ".aAAA000.",
    ".aAgGg00.",
    ".aGGGGG0.",
    ".agG0G0g.",
    ".aGGGGG0.",
    ".aAGgG00.",
    ".aAgGg00.",
    ".aAAA000.",
    ".aAAA000.",
    ".aAA.000.",
    ".aA...00.",
]
KNEE = [
    "..gggg..",
    ".gRRRRg.",
    "gRAAAAAg",
    "gAAgAAAg",
    "gAAAAAAg",
    ".gaaaag.",
]
FOOT = [
    "...aAAAAa...",
    "..aAAAAAAAR.",
    ".aAAAAAAAAAR",
    "gggggggggggg",
]
OX, OY = 5, 13
# stride: foot x offset from the hip and lift, 10-frame cycle; planted (lift 0) feet move -2 px/frame
FOOT_X = [5, 3, 1, -1, -3, -5, -3, 1, 5, 7]
LIFT = [0, 0, 0, 0, 0, 0, 2, 4, 3, 1]
BOB = [1, 1, 0, 0, 0]                            # body sinks on each footfall, period 5
NEAR_SHADE = {}
FAR_SHADE = {"R": "A", "A": "a", "g": "e"}       # far leg sits in shadow


# Hive buildings: black silhouettes rim-lit by the fires, w = flickering windows
SPIRE = [
    "...e...",
    "...e...",
    "...e...",
    "..e0e..",
    "..e0e..",
    ".e000e.",
    ".e0w0e.",
    ".e0w0e.",
    ".e000e.",
    "ee000ee",
    "e00000e",
    "e00000e",
]
CATHEDRAL = [
    "......e......",
    ".....e0e.....",
    "....e000e....",
    "e..e00000e..e",
    "e.e0000000e.e",
    "eee000w000eee",
    "e000ww0ww000e",
    "e00w00w00w00e",
    "e000ww0ww000e",
    "e00000w00000e",
    "e00000000000e",
    "e0w00000000we",
    "e0w00000000we",
    "e00000000000e",
]
ARCH = [  # broken gothic arch: the right half has fallen
    "..eee....",
    ".e000e...",
    "e00e00e..",
    "e0e..e0e.",
    "e0e...ee.",
    "e0e......",
    "e0e......",
    "e0e....e.",
    "e0e...e0e",
    "e0e...e0e",
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
    """30 px tile: each building's last map row repeats down to the ground as its wall."""
    c = np.full((SIZE, HIVE_W), ".", "<U1")
    for rows, top, left in ((SPIRE, 17, 0), (CATHEDRAL, 25, 8), (ARCH, 36, 21)):
        stamp(c, rows, top, left)
        for y in range(top + len(rows), GROUND):   # below the glow line walls are pure silhouette
            stamp(c, rows[-1:] if y < GLOW else [rows[-1].replace("e", "0")], y, left)
    for y in range(42, GROUND - 4, 5):               # a few lit windows down the walls
        for x in (2, 4, 10, 12, 16, 18):
            if c[y, x] == "0" and (x * 3 + y) % 7 < 3:
                c[y:y + 2, x] = "w"
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
        elif ch == "P":                            # reactor pulses
            img[m] = PLASMA[PULSE[i % 5]]
        else:
            img[m] = PAL[ch]


def _tint(rows: list[str], shade: dict) -> list[str]:
    return ["".join(shade.get(ch, ch) for ch in r) for r in rows]


def _part(c: np.ndarray, rows: list[str], top: int, left: int, line: bool = True) -> None:
    """Stamp a part; line=True first cuts a 1 px black outline into whatever lies behind it."""
    if line:
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            stamp(c, ["".join("." if ch == "." else "0" for ch in r) for r in rows], top + dy, left + dx)
    stamp(c, rows, top, left)


def _slab(x0: int, y0: int, x1: int, y1: int, w: int, shade: dict) -> list:
    """An armoured limb segment from (x0, y0) down to (x1, y1): shadowed back, lit front edge."""
    rows = []
    for y in range(y0, y1 + 1):
        cx = x0 + ((x1 - x0) * (y - y0) * 2 + (y1 - y0)) // (2 * max(y1 - y0, 1))
        rows.append((y, cx - w // 2, _tint(["a" + "A" * (w - 2) + "R"], shade)[0]))
    return rows


def _leg(c: np.ndarray, hx: int, hy: int, p: int, shade: dict) -> None:
    fx, lift = hx + FOOT_X[p], LIFT[p]
    ay = GROUND - 4 - lift                         # ankle: top of the foot
    ky = (hy + ay) // 2 - lift // 2                # knee rides up as the foot lifts
    kx = (hx + fx) // 2 + 3 + lift // 2            # and juts forward
    segs = _slab(hx, hy, kx, ky, 6, shade) + _slab(kx, ky, fx, ay, 7, shade)
    for y, x, row in segs:                         # outline the whole leg, then fill it
        for dx in (-1, len(row)):
            stamp(c, ["0"], y, x + dx)
    for y, x, row in segs:
        stamp(c, [row], y, x)
    _part(c, _tint(KNEE, shade), ky - 3, kx - 4)
    _part(c, _tint(FOOT, shade), ay, fx - 6)


def _titan(img: np.ndarray, i: int) -> dict:
    """Draw the Titan with a black keyline; returns gun muzzle positions for the beat effects."""
    p = i % 10
    oy = OY + BOB[i % 5]
    sway = [0, 0, 1, 1, 1, 0, 0, -1, -1, -1][p]   # arms swing against the stride
    c = np.full((SIZE, SIZE), ".", "<U1")
    lx, bx = OX + 18 - sway, OX + 14 + sway
    _part(c, LASER, oy + 15, lx, False)
    _leg(c, OX + 8, oy + 17, (p + 5) % 10, FAR_SHADE)
    _part(c, PELVIS, oy + 13, OX + 4)
    _leg(c, OX + 15, oy + 17, p, NEAR_SHADE)
    _part(c, BANNER, oy + 18, OX + 6 - sway)
    _part(c, REACTOR, oy + 5, OX - 3, False)
    _part(c, CARAPACE, oy, OX, False)
    _part(c, HEAD, oy + 10, OX + 25)
    _part(c, BOLTER, oy + 18, bx)
    _part(c, PAULDRON, oy + 9, OX + 11)
    mask = c != "."
    ring = mask.copy()                              # 1 px black keyline round the whole machine
    ring[1:] |= mask[:-1]
    ring[:-1] |= mask[1:]
    ring[:, 1:] |= mask[:, :-1]
    ring[:, :-1] |= mask[:, 1:]
    img[ring & ~mask] = 0
    _paint(img, c, i, np.zeros((SIZE, SIZE), int))
    return {"laser": (oy + 17, lx + len(LASER[2])),
            "bolter": (oy + 23, bx + len(BOLTER[3]))}


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n`: every motion is built periodic in N, and the test checks frame(N) == frame(0)
    xs = np.arange(SIZE)
    img = np.zeros((SIZE, SIZE, 3))
    img[GLOW:GROUND] = PAL["h"]
    img[50:GROUND] = FIRE[0]
    hx = np.broadcast_to((xs + i) % HIVE_W, (SIZE, SIZE))
    _paint(img, HIVE[:, hx[0]], i, hx)
    for k, tx in enumerate((9, 24)):               # fires at the tower bases ride the hive layer
        for sx in ((tx - i) % HIVE_W + o for o in (-HIVE_W, 0, HIVE_W)):
            _fire(img, GROUND - 1, sx, 6, 8, i, 4 * k)
    rx = np.broadcast_to((xs + 2 * i) % RUB_W, (SIZE, SIZE))
    _paint(img, RUBBLE[:, rx[0]], i, rx)
    for sx in ((34 - 2 * i) % RUB_W + o for o in (-RUB_W, 0)):  # the wreck burns
        _fire(img, GROUND - 5, sx, 5, 7, i, 2)
    for y0, x, k in EMBERS:                        # embers rise 2 px/frame and drift right, wrap every 60 rows
        t = (y0 + 2 * i) % 60
        y = 57 - t
        if 0 <= y < SIZE:
            img[y, (x + t // 15) % SIZE] = FIRE[2 + k]
    for x0, top in TROOPERS:                       # tiny troopers flee left, faster than the ground
        x = (x0 - 3 * i) % 90 - 13
        for r, row in enumerate(TROOPER[(i + x0) % 2]):
            for col, ch in enumerate(row):
                if ch != "." and 0 <= x + col < SIZE:
                    img[top + r, x + col] = PAL[ch]
    guns = _titan(img, i)
    tip_y, tip_x = guns["laser"]
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    for f0 in SHOTS:                               # turbo-laser: charge glow, white core, magenta falloff
        a = i % N - f0
        hit = HIT_X - a                            # the target tower rides the hive layer
        if -2 <= a < 0:
            img[tip_y, tip_x - 2:tip_x] = BEAM[a + 2]
        if 0 <= a < 3:
            core, edge = [(BEAM[2], BEAM[1]), (BEAM[1], BEAM[0]), (BEAM[0], None)][a]
            img[tip_y, tip_x:hit] = core
            if edge:
                img[tip_y - 1, tip_x:hit], img[tip_y + 1, tip_x:hit] = edge, edge
        b = a - 1                                  # the struck tower erupts
        if 0 <= b < 5:
            r = [1, 2, 4, 5, 5][b]
            d2 = (yy - HIT_Y) ** 2 + (xx - hit) ** 2
            img[d2 <= r * r] = [FIRE[4], FIRE[4], FIRE[3], FIRE[2], FIRE[1]][b]
            if b >= 2:
                img[d2 <= (r - 2) ** 2] = FIRE[4]
    if (i - 9) % 15 < 7 and i % 2:                # mega-bolter bursts between the shots
        my, mx = guns["bolter"]
        img[my - 2:my + 3, mx:mx + 2] = FIRE[2]      # star-shaped muzzle flash
        img[my - 1:my + 2, mx:mx + 3] = FIRE[3]
        img[my, mx:mx + 4] = FIRE[4]
        for t in range(3):                         # tracers from the three barrels
            x = mx + 5 + 4 * t + 2 * (i % 3)
            img[my - 2 + 2 * t, x:x + 3] = FIRE[3]   # slices clip at the screen edge
    return np.clip(img, 0, 255).astype(np.uint8)
