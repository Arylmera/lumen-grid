"""Contest and Pixoo constraints + seamless loops. Run: python -m pytest -q"""
import numpy as np
import pytest
from PIL import Image

from ledviz.core import MAX_BYTES, SIZE, save_gif
from ledviz.effects import EFFECTS


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_loop_is_seamless(name):
    """Frame n must be frame 0 exactly, so the GIF's wrap from n-1 to 0 is an ordinary step.
    (A mean-difference check is blind on a pan: every step is already large.)"""
    fn, n, _ = EFFECTS[name]
    assert np.array_equal(fn(n, n), fn(0, n))


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_fits_the_pixoo(name):
    """The Pixoo 64 replays only the first ~30-32 frames. (Colours and motion: the rubric gate.)"""
    fn, n, _ = EFFECTS[name]
    frames = np.stack([fn(i, n) for i in range(n)])
    assert n <= 30
    assert frames.shape[1:] == (SIZE, SIZE, 3) and frames.dtype == np.uint8


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_gif_is_square_and_under_5mb(name, tmp_path):
    fn, n, fps = EFFECTS[name]
    path = save_gif([fn(i, n) for i in range(n)], tmp_path / f"{name}.gif", fps=fps, scale=8)
    with Image.open(path) as im:
        assert im.width == im.height
        assert im.n_frames == n
    assert path.stat().st_size <= MAX_BYTES
