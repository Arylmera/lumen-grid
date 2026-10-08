"""Contest rubric proxy gate (see .superpowers/sdd/global-constraints.md). Every registered
scene must pass every proxy in ledviz.rubric.THRESHOLDS, measured over all its frames.

Scenes with a known-failing proxy are listed in conftest.PENDING, which xfail(strict=True)s just
that (scene, proxy) pair: the suite stays green now, but turns red the moment a listed scene
starts passing everything, as a reminder to drop it from PENDING. Run: python -m pytest -q
"""
from functools import lru_cache

import numpy as np
import pytest

from ledviz.effects import EFFECTS
from ledviz.rubric import THRESHOLDS, metrics, passes
from conftest import PENDING


@lru_cache(maxsize=None)
def _metrics(name: str) -> dict:
    fn, n, _ = EFFECTS[name]
    frames = np.stack([fn(i, n) for i in range(n)])
    return metrics(frames)


CASES = [
    pytest.param(
        name, proxy,
        marks=[pytest.mark.xfail(strict=True, reason=f"{name}: known {proxy} failure, see PENDING")]
        if proxy in PENDING.get(name, ()) else [],
    )
    for name in sorted(EFFECTS)
    for proxy in THRESHOLDS
]


@pytest.mark.parametrize("name,proxy", CASES)
def test_rubric_proxy(name, proxy):
    value = _metrics(name)[proxy]
    op, bound = THRESHOLDS[proxy]
    assert passes(proxy, value), f"{name}: {proxy}={value!r} fails threshold {op} {bound}"
