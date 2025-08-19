from __future__ import annotations

from src.app.math.invariance import check_invariance
from src.app.math.schemas import ProblemSpec
from src.app.math.skills.pythagorean import generate_problem


def test_invariance_correct_spec() -> None:
    """Test that correct specifications pass invariance check."""
    for diff in [1, 2, 3]:
        spec = generate_problem("pythagorean.find_c", diff)
        assert check_invariance(spec, "dummy_stem") is True


def test_invariance_find_leg_skill() -> None:
    """Test invariance check for find_leg skill (covers line 21)."""
    spec = generate_problem("pythagorean.find_leg", 4)
    assert check_invariance(spec, "dummy_stem") is True


def test_invariance_invalid_vars_type():
    """Test that invalid variable types return False."""
    spec = ProblemSpec(
        id="test",
        skill="pythagorean.find_c",
        difficulty=1,
        vars={"a": "invalid", "b": 4, "c": 5},  # string where float expected
        solution={"answer": 5},
    )
    assert check_invariance(spec, "dummy_stem") is False


def test_invariance_missing_vars():
    """Test that missing variables return False."""
    spec = ProblemSpec(
        id="test",
        skill="pythagorean.find_c",
        difficulty=1,
        vars={"a": "invalid"},  # invalid type for conversion to float
        solution={"answer": 5},
    )
    assert check_invariance(spec, "dummy_stem") is False
