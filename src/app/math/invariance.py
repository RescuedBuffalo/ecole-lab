from __future__ import annotations

import math

from .schemas import ProblemSpec


def check_invariance(spec: ProblemSpec, stem_text: str) -> bool:
    """Recompute the expected solution and compare."""
    try:
        a = float(spec.vars.get("a", 0))
        b = float(spec.vars.get("b", 0))
        c = float(spec.vars.get("c", 0))
    except (TypeError, ValueError):
        return False

    expected: float
    if spec.skill == "pythagorean.find_c":
        expected = math.sqrt(a * a + b * b)
    else:
        expected = math.sqrt(c * c - a * a)

    target = float(spec.solution.get("answer", 0))
    return abs(expected - target) < 0.05
