from typing import Literal

from src.app.math.skills.pythagorean import generate_problem
from src.app.math.templater import render_context
from src.app.math.invariance import check_invariance


def test_math_invariance() -> None:
    specs = []
    for diff in [1, 2, 3, 4]:
        skill: Literal["pythagorean.find_c", "pythagorean.find_leg"] = (
            "pythagorean.find_c" if diff < 4 else "pythagorean.find_leg"
        )
        for _ in range(50):
            specs.append(generate_problem(skill, diff))
    for spec in specs:
        item = render_context("neutral_v1", spec, "neutral", "meters")
        assert check_invariance(spec, item.stem)
