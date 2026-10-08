"""Contest constraints + seamless loops. Run: python -m pytest -q"""
import numpy as np
import pytest
from PIL import Image

from ledviz.core import MAX_BYTES, SIZE, save_gif
from ledviz.effects import EFFECTS


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_loop_is_seamless(name):
    fn, n, _ = EFFECTS[name]
    assert np.array_equal(fn(0, n), fn(n, n)), "the frame after the last must equal the first"


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
    path = save_gif([fn(i, n) for i in range(n)], tmp_path / f"{name}.gif", fps=fps, scale=4)
    with Image.open(path) as im:
        assert im.width == im.height
        assert im.n_frames == n
    assert path.stat().st_size <= MAX_BYTES
