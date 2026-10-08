"""Registry of the scenes. Each frame(i, n) -> (64, 64, 3) uint8 is periodic in i with period n,
so every GIF loops with no visible seam (tests/test_effects.py checks the wrap-around step)."""
from .scenes import astartes, necron, ork

EFFECTS = {  # name: (frame fn, frames, fps)
    "astartes": (astartes.frame, 120, 20),
    "necron": (necron.frame, 120, 20),
    "waaagh": (ork.frame, 120, 20),
}
