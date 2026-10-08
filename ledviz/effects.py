"""Registry of the scenes. Each frame(i, n) -> (64, 64, 3) uint8 is periodic in i with period n,
so every GIF loops with no visible seam (tests/test_effects.py checks frame(n) == frame(0))."""
from .scenes import coder, maglev, nave, neon, titan, trench

EFFECTS = {  # name: (frame fn, frames, fps); the Pixoo 64 replays at most ~30 frames
    "nave": (nave.frame, nave.N, 10),
    "trench": (trench.frame, trench.N, 10),
    "maglev": (maglev.frame, maglev.N, 10),
    "neon": (neon.frame, neon.N, 10),
    "titan": (titan.frame, titan.N, 10),
    "coder": (coder.frame, coder.N, 10),
}
