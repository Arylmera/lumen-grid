"""Registry of the scenes. Each frame(i, n) -> (64, 64, 3) uint8 is periodic in i with period n,
so every GIF loops with no visible seam (tests/test_effects.py checks frame(n) == frame(0))."""
from .scenes import coder, neon, titan

EFFECTS = {  # name: (frame fn, frames, fps); the Pixoo 64 replays at most ~30 frames
    "neon": (neon.frame, neon.N, 10),
    "titan": (titan.frame, titan.N, 10),
    "coder": (coder.frame, coder.N, 10),
}
