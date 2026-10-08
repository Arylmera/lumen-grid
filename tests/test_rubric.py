"""Contest rubric proxy gate (see docs/superpowers/plans/2026-10-08-dioramas-v3.md, section
Global Constraints). Every registered scene must pass every proxy in ledviz.rubric.THRESHOLDS,
measured over all its frames.
Run: python -m pytest -q
"""
from functools import lru_cache

import numpy as np
import pytest

from ledviz.effects import EFFECTS
from ledviz.rubric import THRESHOLDS, metrics, passes


@lru_cache(maxsize=None)  # caches each scene's metrics dict for the pytest session
def _metrics(name: str) -> dict:
    fn, n, _ = EFFECTS[name]
    frames = np.stack([fn(i, n) for i in range(n)])
    return metrics(frames)


CASES = [(name, proxy) for name in sorted(EFFECTS) for proxy in THRESHOLDS]


@pytest.mark.parametrize("name,proxy", CASES)
def test_rubric_proxy(name, proxy):
    value = _metrics(name)[proxy]
    op, bound = THRESHOLDS[proxy]
    assert passes(proxy, value), f"{name}: {proxy}={value!r} fails threshold {op} {bound}"
