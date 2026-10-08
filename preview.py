"""Contact-sheet preview for one scene, for eyeballing it before trusting the rubric numbers.

    python preview.py <name> [--out PATH]   # default out/<name>_sheet.png

All 30 frames, 4x nearest-neighbour, laid out 6 columns x 5 rows with a 2 px black gutter.
Also prints the rubric metrics table for the scene.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from ledviz.core import SIZE
from ledviz.effects import EFFECTS
from ledviz.rubric import THRESHOLDS, metrics, passes

SCALE = 4
COLS, ROWS = 6, 5
GUTTER = 2


def _sheet(frames: list[np.ndarray]) -> np.ndarray:
    tile = SIZE * SCALE
    w = COLS * tile + (COLS + 1) * GUTTER
    h = ROWS * tile + (ROWS + 1) * GUTTER
    canvas = np.zeros((h, w, 3), np.uint8)
    for i, frame in enumerate(frames):
        row, col = divmod(i, COLS)
        y = GUTTER + row * (tile + GUTTER)
        x = GUTTER + col * (tile + GUTTER)
        up = np.asarray(Image.fromarray(frame, "RGB").resize((tile, tile), Image.NEAREST))
        canvas[y:y + tile, x:x + tile] = up
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=sorted(EFFECTS))
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    fn, n, _ = EFFECTS[args.name]
    frames = [fn(i, n) for i in range(n)]
    out = args.out or Path("out") / f"{args.name}_sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(_sheet(frames), "RGB").save(out)
    print(f"wrote {out}")

    m = metrics(np.stack(frames))
    print(f"\n{'proxy':<10} {'value':>10} {'threshold':>14}  ok")
    for proxy, (op, bound) in THRESHOLDS.items():
        ok = passes(proxy, m[proxy])
        bound_str = f"{bound:.2f}" if isinstance(bound, float) else str(bound)
        print(f"{proxy:<10} {m[proxy]:>10.4f} {op:>4} {bound_str:>9}  {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
