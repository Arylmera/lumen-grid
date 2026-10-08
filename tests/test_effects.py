"""Contest constraints + seamless loops. Run: python -m pytest -q"""
import numpy as np
import pytest
from PIL import Image

from ledviz.core import MAX_BYTES, SIZE, save_gif
from ledviz.effects import EFFECTS


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_loop_is_seamless(name):
    """The wrap-around step (last frame -> first) must look like any other step: no jump."""
    fn, n, _ = EFFECTS[name]
    frames = [fn(i, n).astype(int) for i in range(n)]
    steps = [np.abs(frames[i + 1] - frames[i]).mean() for i in range(n - 1)]
    wrap = np.abs(frames[0] - frames[-1]).mean()
    assert wrap <= 1.5 * np.median(steps), f"seam jump {wrap:.2f} vs typical step {np.median(steps):.2f}"


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_frames_are_64x64_and_animated(name):
    fn, n, _ = EFFECTS[name]
    a, b = fn(0, n), fn(n // 3, n)
    assert a.shape == (SIZE, SIZE, 3) and a.dtype == np.uint8
    assert a.mean() > 2, "frame is essentially black"
    assert not np.array_equal(a, b), "effect does not move"


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_gif_is_square_and_under_5mb(name, tmp_path):
    fn, n, fps = EFFECTS[name]
    path = save_gif([fn(i, n) for i in range(n)], tmp_path / f"{name}.gif", fps=fps, scale=8)
    with Image.open(path) as im:
        assert im.width == im.height
        assert im.n_frames == n
    assert path.stat().st_size <= MAX_BYTES
