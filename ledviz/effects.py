"""Registry of the scenes. Each frame(i, n) -> (64, 64, 3) uint8 is periodic in i with period n,
so every GIF loops with no visible seam (tests/test_effects.py checks the wrap-around step)."""
from .scenes import nave

EFFECTS = {  # name: (frame fn, frames, fps); the Pixoo 64 replays at most ~30 frames
    "nave": (nave.frame, nave.N, 10),
}
