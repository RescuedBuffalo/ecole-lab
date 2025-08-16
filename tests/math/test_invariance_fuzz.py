from hypothesis import given, strategies as st

from typing import Literal, cast

from src.app.math.invariance import check_invariance
from src.app.math.templater import render_context
from src.app.math.skills.pythagorean import generate_problem


@given(st.integers(min_value=1, max_value=4))
def test_invariance(diff: int) -> None:
    skill = "pythagorean.find_c" if diff < 4 else "pythagorean.find_leg"
    diff_val = diff if diff < 4 else 4
    spec = generate_problem(
        cast(Literal["pythagorean.find_c", "pythagorean.find_leg"], skill), diff_val
    )
    ctx = render_context("neutral_v1", spec, "neutral", "meters")
    assert check_invariance(spec, ctx.stem)
