"""Render every effect to out/.

    python render.py                 # 64x64 GIFs (what the LED panel shows) + 256x256 previews
    python render.py --only terra    # one effect
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ledviz.core import MAX_BYTES, save_gif
from ledviz.effects import EFFECTS

OUT = Path(__file__).parent / "out"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=sorted(EFFECTS))
    ap.add_argument("--preview-scale", type=int, default=4, help="nearest-neighbour upscale for the preview GIF")
    args = ap.parse_args()

    for name, (fn, n, fps) in EFFECTS.items():
        if args.only and name != args.only:
            continue
        frames = [fn(i, n) for i in range(n)]
        for path, scale in ((OUT / f"{name}_64.gif", 1), (OUT / f"{name}_{64 * args.preview_scale}.gif", args.preview_scale)):
            save_gif(frames, path, fps=fps, scale=scale)
            size = path.stat().st_size
            flag = "OK " if size <= MAX_BYTES else "TOO BIG"
            print(f"{flag} {path.name:22s} {size / 1024:8.1f} KiB  {n} frames @ {fps} fps")


if __name__ == "__main__":
    main()
