"""Robot Coder: pair programming with a robot, late at night. It types, runs the tests, they pass.

Built for LED contrast: the room is true black, lit only by the monitor, the RGB keyboard and the
neon trim. Every lit thing is a saturated shape; white is kept to small highlights. Static camera:
the story beats carry the loop.

    window      top right: full moon, twinkling stars, a skyline with lit windows
    monitor     syntax-highlighted code scrolls up 1 px/frame (30-row tile); the newest line types
                itself out behind a blinking cursor. f16 a test pane opens, f22 the screen turns
                into a green PASS with a check mark
    robot       blue, keylined: visor face (blinks, sweats while the tests run, ^ ^ on PASS),
                antenna light, typing with alternating hands, slams Enter at f16, cheers f22-28
    desk        RGB keyboard chasing the Google colours, a rubber duck that hops on PASS, an OIL
                mug with rising steam
    under desk  the robot's tapping foot, its office chair, a server rack with blinking LEDs, and
                the monitor cable carrying data pulses down to the rack
"""
from __future__ import annotations

import numpy as np

from ..core import SIZE, blit, keyline, stamp

N = 30
ENTER, PASS = 16, 22          # beats: Enter is slammed at f16, the tests pass at f22 (to f28)
DESK = 38                     # desk top row

PAL = {
    "0": (0, 0, 0),
    "B": (66, 133, 244), "H": (150, 200, 255), "d": (26, 60, 170),   # robot blue / lit / shadow
    "n": (20, 30, 110), "E": (60, 240, 255), "K": (255, 80, 160),    # visor bezel, face glyphs, blush
    "W": (255, 255, 255),
    "R": (234, 67, 53), "r": (120, 18, 20),                           # Google red / dark red
    "Y": (255, 210, 30), "y": (220, 130, 0), "G": (52, 220, 90),      # yellow / duck shade / green
    "g": (16, 110, 40),                                               # dark green
    "M": (255, 60, 200), "I": (60, 220, 255), "S": (255, 214, 40),    # code: keyword, ident, string
    "C": (60, 230, 90), "P": (255, 140, 40), "u": (60, 70, 200),      # comment, punct, gutter
    "v": (100, 50, 200), "V": (160, 110, 255),                        # monitor violet / highlight
    "o": (200, 90, 20), "O": (255, 150, 40), "q": (110, 40, 8),       # desk top / edge / face
    "k": (50, 30, 110),                                               # keyboard base, rack panels
    "m": (150, 30, 130),                                              # chair
    "s": (130, 170, 255),                                             # steam
    "L": (255, 240, 160),                                             # moon
}
GOOGLE = ["B", "R", "Y", "B", "G", "R"]       # G o o g l e: the keyboard chase, period 6
RAINBOW = ["R", "Y", "G", "E", "B", "M"]       # antenna and confetti on PASS

FONT = {  # 3x5, Z is the ink; I is 1 px wide
    "P": ["ZZ.", "Z.Z", "ZZ.", "Z..", "Z.."], "A": [".Z.", "Z.Z", "ZZZ", "Z.Z", "Z.Z"],
    "S": ["ZZZ", "Z..", "ZZZ", "..Z", "ZZZ"], "T": ["ZZZ", ".Z.", ".Z.", ".Z.", ".Z."],
    "E": ["ZZZ", "Z..", "ZZ.", "Z..", "ZZZ"], "O": ["ZZZ", "Z.Z", "Z.Z", "Z.Z", "ZZZ"],
    "I": ["Z", "Z", "Z", "Z", "Z"], "L": ["Z..", "Z..", "Z..", "Z..", "ZZZ"],
}

HEAD = [  # three-quarter view facing the monitor: ear bolt on the left, visor screen on the right
    ".BBBBBBBBBBBBBB.",
    "BHHHHHHHBBBBBBBB",
    "BHBBBBBBBBBBBBBB",
    "BHdBBnnnnnnnnnnB",
    "BHBBn0000000000n",
    "BBBBn0000000000n",
    "BddBn0000000000n",
    "dHHdn0000000000n",
    "BddBn0000000000n",
    "BBBBn0000000000n",
    "dHdBn0000000000n",
    "dBBBBnnnnnnnnnnB",
    "dBBBBBnBnBnBnBBd",
    ".dddddddddddddd.",
]
FACES = {  # 10x7 glyphs on the visor screen
    "look": ["..........", "....EE..EE", "....EE..EE", "....EE..EE",
             "..........", "......EE..", ".........."],
    "blink": ["..........", "..........", "..........", "....EE..EE",
              "..........", "......EE..", ".........."],
    "focus": ["....EE..EE", "....EE..EE", "..........", "..........",
              "......E...", ".....E.E..", "......E..."],
    "happy": ["..........", "...E...E..", "..E.E.E.E.", "..........",
              ".K.......K", "...E...E..", "....EEE..."],
}
TORSO = [  # behind the desk; chest panel with three status LEDs (g)
    "...BBBBBBBB...",
    ".BBHHHHBBBBBB.",
    "BBHBBBBBBBBBBE",
    "BHBBkkkkkkBBBE",
    "BHBBkgkgkgBBBE",
    "BHBBkkkkkkBBBE",
    "BHBBBBBBBBBBBE",
    "dBBBBBBBBBBBBE",
    "dBBBBBBBBBBBBE",
    "dBBBBBBBBBBBBE",
    "ddBBBBBBBBBBdd",
    "ddBBBBBBBBBBdd",
]
ANTENNA = [".r.", "rrr", ".r.", ".d.", ".d.", ".d.", ".d."]
HAND = ["HH", "BB"]
FLAT = ["HHH", "BBB"]                          # the hand flattened on Enter
FIST = ["HHH", "BBB", "BBd"]
HANDS = {"pump": FIST, "flex": FIST, "slam": FLAT}   # near hand by pose; HAND otherwise

# Arm poses: (shoulder, elbow, hand top-left), screen coords before the PASS bounce
NEAR = {
    "down": ((14, 30), (17, 35), (21, 37)), "up": ((14, 30), (17, 33), (21, 34)),
    "wind": ((14, 30), (19, 31), (21, 27)), "slam": ((14, 30), (18, 35), (20, 38)),
    "pump": ((14, 30), (20, 26), (19, 17)), "flex": ((14, 30), (20, 28), (20, 21)),
}
FAR = {"down": ((17, 31), (22, 34), (27, 37)), "up": ((17, 31), (22, 32), (27, 34)),
       "rest": ((17, 31), (22, 34), (27, 37))}

CODE = [  # (indent, tokens): 10 lines of 3 rows = the 30-row scrolling tile
    (0, "MMM.IIIIII.PP"),
    (2, "CCCCCCCCCC"),
    (2, "MMM.I.MM.IIIII"),
    (4, "MM.III.P.SSSSSSS"),
    (6, "MMMMMM.IIII"),
    (2, "IIII.P.SSSSSSSSS"),
    (0, ""),
    (0, "CCCCCCCCCCCCCC"),
    (0, "MMMMM.IIIIII.P"),
    (2, "IIIII.PSSSSSP"),
]
SCR_X, SCR_Y, SCR_W, SCR_H = 25, 5, 24, 24     # the screen inside the bezel
TYPE_ROW = 18                                  # the line being typed sits here; below is unwritten

CHECK = [
    "...........GG",
    "..........GGG",
    ".........GGG.",
    "GG......GGG..",
    "GGG....GGG...",
    ".GGG..GGG....",
    "..GGGGGG.....",
    "...GGGG......",
    "....GG.......",
]
MUG = [  # handle towards the robot; the label reads OIL
    "..rRRRRRRRRRr",
    "..ryyyyyyyyyr",
    "RRRRRRRRRRRRr",
    "R.R.........r",
    "R.R.........r",
    "R.R.........r",
    "RRR.........r",
    "..R.........r",
    "..RRRRRRRRRRr",
    "...rrrrrrrrr.",
]
DUCK = [  # rubber duck, facing the robot
    "..YYY...",
    ".YY0Y...",
    "OOYYY..Y",
    "..YYYYYY",
    ".YYYYYYY",
    ".YYYYYYy",
    "..yyyyy.",
]
MOON = [".LLL.", "LLsLL", "LLLLL", "LLLsL", ".LLL."]
SKYLINE = [
    ".....uuu.",
    "uuu..uYu.",
    "uYu..u.uu",
    "u.uuuuuYu",
    "uYu.Yu..u",
    "u.u..uY.u",
]
STARS = [(3, 61, 0), (6, 62, 4), (9, 55, 7), (8, 60, 2), (2, 54, 5)]   # (y, x, phase)
SWAY = [0, 0, 1, 1, 0, 0, -1, -1, 0, 0]                                # steam, period 10
RACK_X, RACK_Y = 49, 45
CABLE = [(40, y) for y in range(DESK + 6, 61)] + [(x, 61) for x in range(40, RACK_X)]   # monitor to rack


def _text(c: np.ndarray, s: str, top: int, left: int, ch: str) -> None:
    for letter in s:
        glyph = FONT[letter]
        stamp(c, [row.replace("Z", ch) for row in glyph], top, left)
        left += len(glyph[0]) + 1


def _seg(c: np.ndarray, p0: tuple, p1: tuple, ch: str) -> None:
    """A 2 px thick straight limb from p0 to p1."""
    (x0, y0), (x1, y1) = p0, p1
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for t in range(steps + 1):
        x = x0 + round((x1 - x0) * t / steps)
        y = y0 + round((y1 - y0) * t / steps)
        c[y:y + 2, x:x + 2] = ch


def _keyline(c: np.ndarray, layer: np.ndarray) -> None:
    """Paint a layer over c with a 1 px black outline cut into whatever lies behind."""
    mask = layer != "."
    c[keyline(mask)] = "0"
    c[mask] = layer[mask]


def _beat(i: int) -> str:
    if i < ENTER - 1 or i == N - 1:
        return "type"
    if i < PASS:
        return {ENTER - 1: "wind", ENTER: "slam"}.get(i, "run")
    return "pass"


def _code_tile() -> np.ndarray:
    t = np.full((30, SCR_W), ".", "<U1")
    for k, (indent, toks) in enumerate(CODE):
        if toks:
            t[3 * k:3 * k + 2, 0] = "u"                       # gutter mark
        for col, ch in enumerate(toks):
            t[3 * k:3 * k + 2, 2 + indent + col] = ch
    return t


TILE = _code_tile()


def _screen(i: int, beat: str) -> np.ndarray:
    """The 24x24 screen as chars."""
    s = np.full((SCR_H, SCR_W), ".", "<U1")
    if beat == "pass":
        p = (i - PASS) % N
        s[0, :], s[-1, :], s[:, 0], s[:, -1] = ("G" if p % 2 == 0 else "g",) * 4
        _text(s, "PASS", 3, 5, "G")
        check = CHECK if p > 0 else [r[:7] for r in CHECK]    # the tick draws itself in
        stamp(s, check, 11, 5)
        if p % 2:                                              # glint on the tick
            s[11, 16:18] = "W"
        return s
    scroll = i if beat == "type" else ENTER - 1               # typing stops on the wind-up
    rows = TILE[(np.arange(SCR_H) + scroll) % 30]
    for k, (indent, toks) in enumerate(CODE):
        top = (3 * k - scroll) % 30
        if top > TYPE_ROW + 2:                                 # not written yet
            rows[top:top + 2] = "."
        elif top >= TYPE_ROW:                                  # being typed: reveal 1/3 per frame
            shown = 2 + indent + len(toks) * (TYPE_ROW + 3 - top) // 3
            rows[top:top + 2, shown:] = "."
            if i % 6 < 3:
                rows[top:top + 2, min(shown + 1, SCR_W - 2)] = "W"   # cursor
    s[:] = rows
    if beat in ("slam", "run"):                                # test pane opens on Enter (f16)
        p = (i - ENTER) % N
        s[12:, :] = "."
        s[12, :] = "v"
        _text(s, "TEST", 14, 2, "I")
        s[21:23, 1:1 + 4 * (p + 1) - 2] = "Y" if p < 5 else "G"
    return s


def _monitor(c: np.ndarray, i: int, beat: str) -> None:
    c[3:31, 23:51] = "v"
    c[3, 24:50] = "V"
    c[3:31, 23] = "V"
    c[SCR_Y:SCR_Y + SCR_H, SCR_X:SCR_X + SCR_W] = "0"
    scr = _screen(i, beat)
    m = scr != "."
    c[SCR_Y:SCR_Y + SCR_H, SCR_X:SCR_X + SCR_W][m] = scr[m]
    c[30, 26] = "G" if beat != "run" or i % 2 else "Y"         # power LED
    c[31:37, 35:39] = "v"                                       # stand
    c[31:37, 35] = "V"
    c[37, 31:43] = "v"


def _window(c: np.ndarray, i: int) -> None:
    c[1, 53:64], c[16, 53:64] = "v", "v"
    c[1:17, 53] = "v"
    c[1:17, 63] = "v"
    blit(c, MOON, 3, 55)
    blit(c, SKYLINE, 10, 54)
    for y, x, ph in STARS:
        t = (i + 3 * ph) % 10
        if t < 7:
            c[y, x] = "W" if t < 2 else "s"
    if (i // 5) % 3 == 1:                                       # a window goes dark for a while
        c[12, 55] = "u"


def _steam(c: np.ndarray, i: int) -> None:
    """Two wavy columns; the wave and a gap between puffs both rise 1 px/frame."""
    for x0, ph in ((55, 0), (60, 3)):
        for y in range(19, 28):
            k = (y + i + ph) % 10
            if k:
                c[y, x0 + SWAY[k]] = "s"


def _robot(c: np.ndarray, i: int, beat: str) -> None:
    lift = -(i % 2 == 0) if beat == "pass" else 0              # hops on PASS
    body = np.full((SIZE, SIZE), ".", "<U1")
    blit(body, TORSO, 26 + lift, 3)
    for n, x in enumerate((8, 10, 12)):                         # chest LEDs run a little scan
        body[30 + lift, x] = "G" if (i + n) % 3 == 0 else "g"
    blit(body, HEAD, 13 + lift, 2)
    nod = 1 if beat == "type" and i % 6 in (2, 3) else 0        # nods along while typing
    if nod:
        body[13:27] = np.roll(body[13:27], 1, axis=0)
        body[13] = "."
    face = {"type": "blink" if i % N in (8, 26) else "look", "wind": "look", "slam": "focus",
            "run": "focus", "pass": "happy"}[beat]
    blit(body, FACES[face], 17 + lift + nod, 7)
    blit(body, ANTENNA, 6 + lift + nod, 7)
    if beat == "run" and (i - ENTER) % N >= 2:                  # a nervous drop of sweat runs down
        y = 14 + (i - ENTER) % N                                # a teardrop on the visor side
        body[y:y + 2, 18:20] = "E"
        body[y - 1, 18] = "E"
        body[y, 18] = "W"
    _keyline(c, body)
    # antenna light: slow blink; rainbow party on PASS
    ay, ax = 7 + lift + nod, 8
    if beat == "pass":
        c[ay - 1:ay + 2, ax], c[ay, ax - 1:ax + 2] = RAINBOW[i % 6], RAINBOW[i % 6]
    else:
        col = "R" if i % 10 < 3 or beat == "run" and i % 2 else "r"
        c[ay - 1:ay + 2, ax], c[ay, ax - 1:ax + 2] = col, col
        c[ay, ax] = "W" if col == "R" else "r"


def _arms(c: np.ndarray, i: int, beat: str) -> None:
    lift = -(i % 2 == 0) if beat == "pass" else 0
    if beat == "type":
        near, far = ("down", "up") if i % 2 == 0 else ("up", "down")
    elif beat == "pass":
        near, far = ("pump" if i % 2 == 0 else "flex"), "rest"
    else:
        near, far = {"wind": "wind", "slam": "slam"}.get(beat, "down"), "rest"
    for pose, shade, hi in ((FAR[far], "d", "B"), (NEAR[near], "B", "H")):
        arm = np.full((SIZE, SIZE), ".", "<U1")                 # each arm keylined on its own
        (sx, sy), (ex, ey), (hx, hy) = pose
        dy = lift if shade == "B" else 0
        _seg(arm, (sx, sy + dy), (ex, ey + dy), shade)
        _seg(arm, (ex, ey + dy), (hx, hy + dy), shade)
        lit = (arm != ".") & np.vstack([np.ones((1, SIZE), bool), arm[:-1] == "."])
        arm[lit] = hi                                           # top edge lit, like a tube
        if shade == "B":                                        # shoulder ball
            blit(arm, [".B.", "BHB", ".B."], sy - 1 + dy, sx - 1)
        rows = HAND if shade == "d" else HANDS.get(near, HAND)
        blit(arm, [r.translate(str.maketrans({"H": hi, "B": shade})) for r in rows], hy + dy, hx)
        _keyline(c, arm)
    if beat == "type":                                          # the struck key lights up
        c[39, NEAR["down"][2][0] if i % 2 == 0 else FAR["down"][2][0] + 1] = "W"
    if beat == "slam":                                          # the Enter key goes off
        c[39, 23:25] = "W"                                      # the Enter key flashes
        for ray in (((34, 30), (33, 31)), ((36, 30), (36, 31))):   # in clear black, right of the far hand
            for y, x in ray:
                c[y, x] = "Y"


def _confetti(c: np.ndarray, i: int) -> None:
    for k, (x, y0) in enumerate(((1, 0), (4, -5), (12, 2), (16, -3), (20, 0), (7, -1), (2, -9), (18, -8))):
        y = y0 + 2 * ((i - PASS) % N)                               # 2 px/frame, only during PASS
        if 0 <= y < 11:
            c[y:y + 2, x:x + 2] = RAINBOW[(k + i) % 6]


def _keyboard(c: np.ndarray, i: int, beat: str) -> None:
    """Lies on the desk top: two rows of keys in a colour chase that runs to the right."""
    c[37:41, 17:33] = "k"
    for x in range(18, 32):
        c[38, x] = GOOGLE[(x - i) % 6] if x % 2 == 0 else "k"
        c[39, x] = GOOGLE[(x + 1 - i) % 6]
    if beat == "pass":                                          # the whole board flashes in time
        c[38:40, 18:32] = GOOGLE[i % 6]


def _desk(c: np.ndarray) -> None:
    c[DESK:DESK + 3, :] = "o"
    c[DESK + 3, :] = "O"
    c[DESK + 4:DESK + 6, :] = "q"
    c[DESK + 6:63, 1:3] = "q"                                   # desk leg


def _under(c: np.ndarray, i: int) -> None:
    for (x, y) in CABLE:                                        # the monitor's cable
        c[y, x] = "v"
    for k in (0, 10, 20):                                       # data pulses run down to the rack
        x, y = CABLE[(i + k) * len(CABLE) // N % len(CABLE)]
        c[y, x] = "E"
    c[20:DESK, 0:2] = "m"                                       # chair: back behind the robot,
    c[19, 0] = "m"
    c[DESK + 6:59, 8:10] = "m"                                  # gas lift, star base, wheels
    c[59, 4:14] = "m"
    for x in (4, 8, 12):
        c[61, x:x + 2] = "v"
    tap = 1 if i % 6 < 2 and i % N < PASS else 0                # the robot taps its foot
    for x, shade, hi, toe in ((18, "d", "d", 23), (14, "B", "H", 20)):   # far leg, then near
        leg = np.full((SIZE, SIZE), ".", "<U1")
        up = tap if shade == "B" else 0
        leg[DESK + 6:57, x:x + 3] = shade                       # shin
        leg[DESK + 6:57, x] = hi
        blit(leg, [".BBB.", "BHBBB", ".BBB."], DESK + 5, x - 1)   # knee
        leg[56 - up, x:x + 3] = "n" if shade == "B" else "0"    # ankle joint
        leg[57 - up:60 - up, x - 1:toe] = shade                 # boot, toe towards the desk
        leg[57 - up, x:toe - 1] = hi
        leg[57 - up, x - 1] = "."
        if shade == "d":
            leg[leg == "B"], leg[leg == "H"] = "d", "d"
        _keyline(c, leg)
    # server rack: four units, each with LEDs on their own beat
    c[RACK_Y:62, RACK_X:63] = "k"
    c[RACK_Y, RACK_X:63] = "V"
    c[RACK_Y:62, RACK_X] = "v"
    c[RACK_Y:62, 62] = "v"
    for u in range(4):
        y = RACK_Y + 2 + 4 * u
        c[y + 2, RACK_X + 1:62] = "v"
        for n, (col, per, on) in enumerate((("G", 2, 1), ("G", 3, 1), ("Y", 5, 2), ("R", 15, 3))):
            if (i + 4 * u + n) % per < on:
                c[y, RACK_X + 2 + 2 * n] = col
        c[y, 58:61] = "u"
        c[y, 58 + (i + u) % 3] = "E"                            # disk activity
    c[63, :] = "u"                                              # the floor


def frame(i: int, n: int = N) -> np.ndarray:
    # no `i %= n` up front: continuous motion is periodic in N by construction; only the story
    # beats (and offsets measured from a beat) read the loop clock i % N
    beat = _beat(i % N)
    c = np.full((SIZE, SIZE), ".", "<U1")
    _window(c, i)
    _steam(c, i)
    _monitor(c, i, beat)
    _under(c, i)
    _robot(c, i, beat)
    _desk(c)
    _keyboard(c, i, beat)
    blit(c, MUG, 28, 51)
    _text(c, "OIL", 31, 54, "Y")
    hop = 2 if beat == "pass" and i % 2 == 0 else 0
    blit(c, DUCK, 31 - hop, 43)
    _arms(c, i, beat)
    if beat == "pass":
        _confetti(c, i)
    img = np.zeros((SIZE, SIZE, 3), np.uint8)
    for ch in np.unique(c):
        if ch != ".":
            img[c == ch] = PAL[ch]
    return img
