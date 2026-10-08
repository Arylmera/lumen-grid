"""Contest rubric proxies (see docs/superpowers/plans/2026-10-08-dioramas-v3.md, section Global
Constraints) computed over a clip's frames. `metrics()` returns the raw numbers; `THRESHOLDS`
holds the pass/fail bar for each."""
from __future__ import annotations

import numpy as np

# proxy -> (comparison, bound). "ge"/"le"/"gt" against the measured value.
THRESHOLDS = {
    "black": ("ge", 0.45),        # at least 0.45 of pixels are exactly (0,0,0)
    "dim": ("le", 0.05),          # at most 0.05 of pixels have max channel in [1, 23]
    "saturation": ("ge", 0.70),   # mean HSV saturation of lit pixels (max channel >= 24)
    "vivid": ("ge", 0.10),        # fraction with saturation > 0.6 and max channel > 120
    "peak": ("ge", 230.0),        # 95th-percentile max channel of lit pixels
    "motion": ("ge", 3.0),        # mean absolute frame-to-frame difference, wrap step included
    "min_step": ("gt", 0.0),      # smallest mean step between consecutive frames, wrap included (no duplicates)
    "colours": ("le", 64),        # unique RGB colours across all frames
}


def metrics(frames: np.ndarray) -> dict:
    """frames: (n, 64, 64, 3) uint8. Returns the measured value for every proxy in THRESHOLDS."""
    frames = np.asarray(frames)
    maxc = frames.max(axis=-1).astype(float)
    minc = frames.min(axis=-1).astype(float)
    lit = maxc >= 24

    black = float((maxc == 0).mean())
    dim = float(((maxc >= 1) & (maxc <= 23)).mean())

    sat = np.zeros_like(maxc)
    np.divide(maxc - minc, maxc, out=sat, where=maxc > 0)
    saturation = float(sat[lit].mean()) if lit.any() else 0.0
    vivid = float(((sat > 0.6) & (maxc > 120)).mean())
    peak = float(np.percentile(maxc[lit], 95)) if lit.any() else 0.0

    # cyclic: the last step is the wrap from frame n-1 to frame 0, so a stutter at the loop point fails
    steps = np.abs(np.roll(frames, -1, 0).astype(int) - frames.astype(int)).mean(axis=(1, 2, 3))
    motion = float(steps.mean()) if len(steps) else 0.0
    min_step = float(steps.min()) if len(steps) else 0.0

    colours = int(len(np.unique(frames.reshape(-1, 3), axis=0)))

    return {
        "black": black, "dim": dim, "saturation": saturation, "vivid": vivid,
        "peak": peak, "motion": motion, "min_step": min_step, "colours": colours,
    }


def passes(proxy: str, value: float) -> bool:
    op, bound = THRESHOLDS[proxy]
    if op == "ge":
        return value >= bound
    if op == "le":
        return value <= bound
    if op == "gt":
        return value > bound
    raise ValueError(op)
