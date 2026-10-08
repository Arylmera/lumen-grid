"""PENDING: scene -> set of currently-failing check names (rubric proxy names, or "seam" for the
loop-seam test). Shared by test_effects.py and test_rubric.py so both apply xfail(strict=True)
off the same list. Each task that fixes a scene removes its failing names here; strict=True means
a listed scene that starts passing everything turns the suite red as a reminder to update this.
"""

PENDING = {
    "neon": {"seam"},                                          # fixed in Task 2
    "titan": {"seam"},                                          # fixed in Task 3
    "nave": {"black", "dim", "saturation", "peak"},             # removed in Task 5
    "trench": {"black", "dim", "saturation", "vivid", "peak"},  # removed in Task 5
    "maglev": {"black", "dim", "saturation", "vivid"},          # removed in Task 5
}
