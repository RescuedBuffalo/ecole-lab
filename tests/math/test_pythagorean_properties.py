from __future__ import annotations

import pytest
from src.app.math.skills.pythagorean import generate_problem


def test_pythagorean_find_c_difficulty_1():
    """Test difficulty 1 for find_c skill."""
    prob = generate_problem("pythagorean.find_c", 1)
    assert prob.skill == "pythagorean.find_c"
    assert prob.difficulty == 1
    assert "a" in prob.vars and "b" in prob.vars and "c" in prob.vars


def test_pythagorean_find_c_difficulty_2():
    """Test difficulty 2 for find_c skill."""
    prob = generate_problem("pythagorean.find_c", 2)
    assert prob.skill == "pythagorean.find_c"
    assert prob.difficulty == 2


def test_pythagorean_find_c_difficulty_3():
    """Test difficulty 3 for find_c skill."""
    prob = generate_problem("pythagorean.find_c", 3)
    assert prob.skill == "pythagorean.find_c"
    assert prob.difficulty == 3


def test_pythagorean_find_leg_difficulty_4():
    """Test difficulty 4 for find_leg skill."""
    prob = generate_problem("pythagorean.find_leg", 4)
    assert prob.skill == "pythagorean.find_leg"
    assert prob.difficulty == 4


def test_pythagorean_find_c_invalid_difficulty():
    """Test that invalid difficulty for find_c raises ValueError."""
    with pytest.raises(ValueError, match="difficulty 1-3 for find_c"):
        generate_problem("pythagorean.find_c", 5)


def test_pythagorean_find_leg_invalid_difficulty():
    """Test that invalid difficulty for find_leg raises ValueError."""
    with pytest.raises(ValueError, match="difficulty must be 4 for find_leg"):
        generate_problem("pythagorean.find_leg", 2)


def test_pythagorean_unknown_skill():
    """Test that unknown skill raises ValueError."""
    with pytest.raises(ValueError, match="unknown skill"):
        generate_problem("unknown.skill", 1)  # type: ignore[arg-type]
