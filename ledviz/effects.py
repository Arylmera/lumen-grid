"""Ave Imperator: a gilded double-headed eagle in a gothic chapel, for a 64x64 LED panel.

The effect is a pure function frame(i, n) -> (64, 64, 3) uint8, periodic in i with period n,
so the GIF loops with no visible seam: frame(n, n) == frame(0, n). The tests assert it.

Layers, back to front:
  stone wall -> lancet stained-glass window (shimmering) -> god rays and dust
  -> altar -> candles (flicker + glow) -> embers rising
  -> the eagle (procedural pixel sprite, gold shading, sweeping glint, skull with pulsing eyes)
  -> purity seal (red wax, parchment strips swaying)
"""
from __future__ import annotations

import numpy as np

from .core import SIZE, to_frame

TAU = 2 * np.pi
_yy, _xx = np.mgrid[0:SIZE, 0:SIZE].astype(float)
CX = (SIZE - 1) / 2                     # 31.5: the eagle is mirror-symmetric about this line


# =========================================================================== the eagle
# Built on the left half (c = 0..31, 31 touching the centre line) and mirrored.
# Feathers are painted as capsules, back to front, each with its own dark outline, so the
# layering reads at 64x64. LEVEL is a 0..1 brightness fed through the gold ramp.
EAGLE_TOP = 9


def _seg_dist(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    t = np.clip(((px - ax) * abx + (py - ay) * aby) / (abx * abx + aby * aby), 0, 1)
    return np.hypot(px - (ax + t * abx), py - (ay + t * aby)), t


def _build_eagle() -> tuple[np.ndarray, np.ndarray]:
    h = SIZE // 2
    py, px = np.mgrid[0:SIZE, 0:h].astype(float)
    px, py = px + 0.5, py + 0.5 - EAGLE_TOP          # pixel centres, sprite-local y
    mask = np.zeros((SIZE, h), bool)
    level = np.zeros((SIZE, h))

    def feather(a, b, w, base, root_bonus=0.15, ridge=True):
        d, t = _seg_dist(px, py, *a, *b)
        # taper: full width at the root, pointed at the tip
        wt = w * (1 - 0.55 * t ** 2)
        inside = d <= wt
        edge = inside & (d > wt - 1.0)
        lv = base + root_bonus * (1 - t)
        if ridge:                                    # bright quill down the middle
            lv = lv + 0.15 * (d < 0.5)
        level[inside] = np.where(edge[inside], 0.06, lv[inside])
        mask[inside] = True

    # arm of the wing: shoulder -> wrist, raised outward
    shoulder, wrist = np.array([25.0, 12.0]), np.array([7.0, 3.0])
    def on_arm(f):
        return tuple(wrist + (shoulder - wrist) * f)

    # primaries: long, fanning from steeply-outward (tip) to straight down (inner)
    n_p = 6
    for k in range(n_p):                             # outermost first, inner ones overlap it
        f = 0.02 + k / (n_p - 1) * 0.78
        root = on_arm(f)
        ang = np.deg2rad(-15 + k * 3.2)              # 0 = straight down, negative = outward
        length = 20 - k * 1.6
        tip = (root[0] + np.sin(ang) * length, root[1] + np.cos(ang) * length)
        feather(root, tip, 2.3, 0.55 - k * 0.015)
    # secondary coverts: two rows of short rounded feathers over the primaries' roots
    for row, (ln, lv) in enumerate(((7.0, 0.68),)):
        n_c = 6
        for k in range(n_c):
            f = 0.08 + k / (n_c - 1) * 0.84
            root = on_arm(f)
            root = (root[0], root[1] + row * 2.2)
            ang = np.deg2rad(-20 + k * 3)
            tip = (root[0] + np.sin(ang) * ln, root[1] + np.cos(ang) * ln)
            feather(root, tip, 2.0, lv, root_bonus=0.1, ridge=False)
    # leading edge of the wing: a thick bright bar
    feather(tuple(wrist + np.array([-2.0, -0.5])), tuple(shoulder), 2.0, 0.85, root_bonus=-0.1, ridge=False)

    # tail: three fanned feathers per side under the body
    for k in range(3):
        ang = np.deg2rad(-6 - k * 16)
        root = (31.5 - k * 1.2, 25.0)
        tip = (root[0] + np.sin(ang) * 9, root[1] + np.cos(ang) * 9)
        feather(root, tip, 2.0, 0.5 - k * 0.05)
    # legs and talons
    for tx in (24.0, 26.0):                       # talons gripping under the breast
        feather((27.5, 24.5), (tx, 28.0), 1.1, 0.3, ridge=False)
    # body: armoured breast
    d = np.hypot((px - 32.0) / 5.6, (py - 17.0) / 10.5)
    body = d <= 1
    level[body] = 0.6 + 0.12 * ((py[body].astype(int) % 3) == 0) - 0.15 * (py[body] - 17) / 10
    level[body & (d > 1 - 1.0 / 5.6) & (px < 31)] = 0.06
    mask |= body
    # neck: from the chest up and out to the head
    feather((29.5, 12.0), (23.5, 4.0), 2.6, 0.65, root_bonus=-0.05, ridge=False)
    # head
    hd = np.hypot((px - 22.5) / 4.2, (py - 2.6) / 3.4)
    head = hd <= 1
    level[head] = 0.82 - 0.08 * (py[head] - 2.6) / 3.4
    level[head & (hd > 0.74)] = 0.06
    mask |= head
    # hooked beak: polished, darker hook tip
    beak = {1: (16, 19), 2: (14, 19), 3: (13, 18), 4: (13, 16), 5: (13, 15), 6: (14, 14)}
    for yy, (c0, c1) in beak.items():
        r = EAGLE_TOP + yy
        for c in range(c0, c1 + 1):
            mask[r, c] = True
            level[r, c] = 0.95 if yy <= 3 and c > c0 else 0.3
    for (r, c) in ((EAGLE_TOP + 3, 19), (EAGLE_TOP + 4, 17)):   # mouth line
        level[r, c] = 0.06

    lab = np.concatenate([mask, mask[:, ::-1]], axis=1)
    lev = np.concatenate([level, level[:, ::-1]], axis=1)
    return lab, lev


EAGLE_MASK, _EAGLE_RAW = _build_eagle()
EAGLE = EAGLE_MASK.astype(int)


def _dilate(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask, 1)
    return p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def _edge(mask: np.ndarray) -> np.ndarray:
    """Mask pixels touching a non-mask pixel (4-neighbourhood)."""
    p = np.pad(mask, 1)
    return mask & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


EAGLE_EDGE = EAGLE_MASK & (_EAGLE_RAW <= 0.07)   # the painted outlines
EAGLE_HALO = _dilate(_dilate(EAGLE_MASK)) & ~EAGLE_MASK   # dark keyline that lifts it off the glass

# gold ramp: 0 = burnt bronze outline ... 1 = white-hot highlight
GOLD = np.array([(45, 20, 4), (110, 55, 10), (175, 110, 25), (225, 165, 45), (255, 215, 95), (255, 248, 205)], float)


def _gold(level: np.ndarray) -> np.ndarray:
    level = np.clip(level, 0, 1) * (len(GOLD) - 1)
    lo = np.floor(level).astype(int)
    hi = np.minimum(lo + 1, len(GOLD) - 1)
    f = (level - lo)[..., None]
    return GOLD[lo] * (1 - f) + GOLD[hi] * f


# light falls from the window above: brighter at the top of the sprite
_EAGLE_LEVEL = np.where(_EAGLE_RAW > 0.07, _EAGLE_RAW + 0.12 - (_yy - EAGLE_TOP) / 90, _EAGLE_RAW)

# eyes: one red pixel per head
_EYES = [(EAGLE_TOP + 2, 21), (EAGLE_TOP + 2, SIZE - 1 - 21)]

# skull on the chest (left half, mirrored): '#' bone, 'o' eye socket, 'n' nose, 't' tooth gap
_SKULL = [
    "..###",
    ".####",
    "#####",
    "#oo##",
    "#oo##",
    ".###n",
    "..###",
    "..#t#",
]
SKULL_TOP = EAGLE_TOP + 12
SKULL = np.full((SIZE, SIZE), "", dtype="<U1")
for _r, _row in enumerate(_SKULL):
    for _c, _ch in enumerate(_row):
        if _ch != ".":
            SKULL[SKULL_TOP + _r, 27 + _c] = _ch
            SKULL[SKULL_TOP + _r, SIZE - 1 - (27 + _c)] = _ch
SKULL_MASK = SKULL != ""
SKULL_EDGE = _dilate(SKULL_MASK) & ~SKULL_MASK


# =========================================================================== backdrop
def _lancet(w: float, r: float, spring: float) -> np.ndarray:
    """Pointed gothic arch: two circles of radius r, sides vertical below the springing line."""
    off = r - w
    in_arc = (np.hypot(_xx - (CX + off), _yy - spring) <= r) & (np.hypot(_xx - (CX - off), _yy - spring) <= r)
    sides = (np.abs(_xx - CX) <= w) & (_yy >= spring)
    return in_arc | sides


WINDOW = _lancet(w=24, r=33, spring=33) & (_yy < 55)
FRAME = _dilate(_dilate(WINDOW)) & ~WINDOW & (_yy < 55)

# diamond quarry glass with lead cames
LEAD = WINDOW & (((_xx + _yy) % 9 == 0) | ((_xx - _yy) % 9 == 0))
_pane = ((_xx + _yy) // 9 + (_xx - _yy) // 9).astype(int) % 5
GLASS = np.array([(120, 10, 18), (25, 30, 120), (140, 15, 25), (150, 95, 15), (20, 70, 90)], float)
_PANE_PHASE = (np.sin((_xx + _yy) // 9 * 12.9898 + (_xx - _yy) // 9 * 78.233) * 43758.5453) % 1.0

# stone wall: offset ashlar blocks
_brick_row = (_yy // 5).astype(int)
_mortar = ((_yy % 5) == 0) | (((_xx + (_brick_row % 2) * 4) % 8) == 0)
STONE = np.where(_mortar[..., None], np.array([10, 9, 12.0]), np.array([30, 26, 34.0]))
STONE = STONE * (0.85 + 0.15 * ((_xx * 7 + _yy * 13) % 5) / 4)[..., None]

ALTAR_Y = 55

# servo-skull sprite: k outline, b bone, s shade, e socket, m brass implant, a antenna
SERVO = [
    "...a...",
    ".kbbbk.",
    "kbbbbbk",
    "kmrbebk",
    "kbbsbbk",
    ".kbtbk.",
    "..ktk..",
]
SERVO_COL = {"k": (25, 18, 14), "b": (225, 215, 185), "s": (150, 140, 120), "e": (20, 10, 10),
             "m": (200, 140, 40), "a": (160, 160, 175), "t": (120, 110, 90), "r": (255, 30, 10)}

# candles: (centre x, top y of wax)
CANDLES = [(6, 44), (57, 44), (12, 48), (51, 48)]

# embers: deterministic, each rises an integer number of laps per loop
_er = np.random.default_rng(1440)
_N_EMB = 26
_emb_x = _er.uniform(2, 62, _N_EMB)
_emb_y0 = _er.uniform(0, 64, _N_EMB)
_emb_laps = _er.choice([1, 2], _N_EMB)
_emb_wob = _er.uniform(0, TAU, _N_EMB)

# dust motes in the light shafts
_N_DUST = 18
_dust_x = _er.uniform(14, 50, _N_DUST)
_dust_y0 = _er.uniform(0, 64, _N_DUST)
_dust_ph = _er.uniform(0, TAU, _N_DUST)


def _add(img: np.ndarray, y: int, x: int, rgb, a: float = 1.0) -> None:
    if 0 <= y < SIZE and 0 <= x < SIZE:
        img[y, x] = img[y, x] * (1 - a) + np.asarray(rgb, float) * a


def _glow(img: np.ndarray, cy: float, cx: float, radius: float, rgb, strength: float) -> None:
    g = np.exp(-((_xx - cx) ** 2 + (_yy - cy) ** 2) / (2 * radius ** 2)) * strength
    img += g[..., None] * np.asarray(rgb, float)


def aquila(i: int, n: int) -> np.ndarray:
    ph = (i % n) / n
    t = TAU * ph
    img = STONE.copy()

    # --- stained glass, each pane breathing on its own phase (one breath per loop)
    breath = 0.55 + 0.25 * np.sin(t + _PANE_PHASE * TAU)
    sky = np.clip(1.2 - (_yy - 5) / 60, 0.5, 1.2)       # brighter near the top of the window
    glass = GLASS[_pane] * (breath * sky)[..., None]
    img = np.where(WINDOW[..., None], glass, img)
    img[LEAD] = (8, 6, 6)
    img[FRAME] = (60, 54, 62)
    img[WINDOW & (np.abs(_xx - CX) < 1)] = (55, 50, 58)  # central mullion
    img[WINDOW & (_yy == 33)] = (55, 50, 58)             # transom bar

    # --- god rays: soft diagonal shafts that slowly pulse
    shaft = np.clip(np.sin((_xx - CX) * 0.35 + _yy * 0.12), 0, 1) ** 6
    ray = shaft * np.clip((_yy - 18) / 40, 0, 1) * (0.5 + 0.2 * np.sin(t)) * (np.abs(_xx - CX) < 26)
    img += ray[..., None] * np.array([70, 50, 25])

    # dust drifting down through the light
    for k in range(_N_DUST):
        y = (_dust_y0[k] + ph * 64) % 64
        x = _dust_x[k] + 1.5 * np.sin(t + _dust_ph[k])
        _add(img, int(y), int(x), (255, 225, 170), 0.35)

    # --- altar: dark marble slab with a gold trim line
    img[ALTAR_Y:] = (18, 12, 14)
    img[ALTAR_Y] = (150, 100, 30)
    img[ALTAR_Y + 1] = (70, 45, 15)
    img[ALTAR_Y + 4, ::4] = (90, 60, 20)

    # --- candles: cream wax with drips, flickering flame, warm glow
    for k, (cx, top) in enumerate(CANDLES):
        img[top:ALTAR_Y, cx - 1:cx + 2] = (205, 190, 160)
        img[top:ALTAR_Y, cx - 1] = (150, 135, 110)       # shadowed side
        img[top:ALTAR_Y, cx + 1] = (235, 225, 200)       # lit side
        _add(img, top + 2, cx + 2, (220, 205, 175))     # wax drip
        _add(img, top + 3, cx + 2, (190, 175, 150))
        flick = 0.5 + 0.5 * np.sin(4 * t + k * 1.7) * np.sin(7 * t + k)  # integer harmonics: loops
        h = 3 + int(round(flick * 2))
        _glow(img, top - 2, cx, 4.5, (255, 130, 30), 0.35 + 0.15 * flick)
        for dy in range(h):
            col = (255, 250, 220) if dy == 0 else ((255, 200, 60) if dy < h - 1 else (230, 90, 20))
            sway = int(round(np.sin(5 * t + k) * 0.6 * dy / 3))
            _add(img, top - 1 - dy, cx + sway, col)
        _add(img, top - 1, cx - 1, (255, 150, 40), 0.6)
        _add(img, top - 1, cx + 1, (255, 150, 40), 0.6)

    # --- embers rising from the candles
    for k in range(_N_EMB):
        y = (_emb_y0[k] - ph * 64 * _emb_laps[k]) % 64
        x = _emb_x[k] + 1.2 * np.sin(2 * t * _emb_laps[k] + _emb_wob[k] + y * 0.2)
        fade = np.clip(y / 64, 0.15, 1)
        _add(img, int(y), int(x), (255, 120 + 80 * fade, 30), 0.85 * fade)

    # --- the eagle
    img[EAGLE_HALO] *= 0.25
    gold = _gold(_EAGLE_LEVEL)
    # glint: a bright diagonal band sweeps across during the first 35% of the loop, then rests
    sweep = (ph / 0.35) * 1.6 - 0.3
    d = (_xx + _yy * 0.6) / (SIZE * 1.6) - sweep
    glint = np.exp(-(d / 0.035) ** 2) * (ph < 0.35)
    gold = gold + glint[..., None] * np.array([120, 110, 80]) * ~EAGLE_EDGE[..., None]
    img = np.where(EAGLE_MASK[..., None], gold, img)
    for (ey, ex) in _EYES:
        img[ey, ex] = (255, 30, 20)

    # --- skull on the chest, eye sockets burning red
    pulse = 0.55 + 0.45 * np.sin(2 * t)
    img[SKULL_EDGE & ~EAGLE_EDGE] = (40, 25, 15)
    img[SKULL == "#"] = (230, 220, 190)
    img[(SKULL == "n") | (SKULL == "t")] = (60, 40, 30)
    img[SKULL == "o"] = np.array([255, 40, 20]) * pulse + np.array([40, 0, 0]) * (1 - pulse)
    _glow(img, SKULL_TOP + 3.5, CX, 3.0, (255, 20, 0), 0.25 * pulse)

    # --- purity seal: red wax disc under the tail, two parchment strips swaying
    sy, sr = 48.0, 3.2
    rr = np.hypot(_xx - CX, _yy - sy)
    disc = rr <= sr
    img[(rr <= sr + 1) & ~disc] *= 0.3
    img[disc] = (165, 18, 22)
    img[disc & (np.abs(rr - 1.9) < 0.45)] = (110, 8, 12)                            # stamped ring
    img[disc & (np.hypot(_xx - CX + 1.5, _yy - sy + 1.5) <= 0.9)] = (240, 90, 80)   # wax highlight
    for side, x0 in ((-1, 28), (1, 33)):
        for y in range(51, 63):
            depth = (y - 51) / 11
            sway = int(round(np.sin(t + side * 0.8) * 1.8 * depth ** 2))  # bends, never zigzags
            for dx in range(3):
                ink = (y % 2 == 1) and dx == 1 and 52 < y < 61
                col = (110, 80, 55) if ink else ((235, 215, 165), (215, 195, 145), (165, 145, 105))[dx]
                _add(img, y, x0 + dx + sway, col)

    # --- servo-skull: hovers in a slow figure-eight, bionic eye sweeping, anti-grav glow below
    sx = 14 + 4 * np.sin(t)
    sy_ = 38 + 2.5 * np.sin(2 * t)
    ox, oy = int(round(sx)), int(round(sy_))
    _glow(img, oy + 7, ox + 3, 2.4, (80, 160, 255), 0.55)
    for r, row in enumerate(SERVO):
        for c, ch in enumerate(row):
            if ch != ".":
                _add(img, oy + r, ox + c, SERVO_COL[ch])
    _add(img, oy + 3, ox + 2, np.array([255, 40, 10]) * pulse + np.array([90, 0, 0]) * (1 - pulse))
    cable = int(round(np.sin(3 * t)))                 # dangling mechadendrite
    _add(img, oy + 7, ox + 3, (90, 90, 100))
    _add(img, oy + 8, ox + 3 + cable, (70, 70, 80))

    return to_frame(img)


EFFECTS = {
    "aquila": (aquila, 120, 20),   # name: (fn, frames, fps)
}
