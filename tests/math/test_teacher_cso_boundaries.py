from src.app.math.teacher_math import evaluate_math_item
from src.app.math.cso_math import policy_check


def test_teacher_rejects_long_stem() -> None:
    stem = "Sentence one. Sentence two. Sentence three."
    result = evaluate_math_item(stem, "Q", "7-9")
    assert result.status != "pass"


def test_teacher_requires_cue() -> None:
    stem = "Two lines meet."  # no right angle cue
    result = evaluate_math_item(stem, "Q", "7-9")
    assert result.status != "pass"


def test_cso_blocks_forbidden_terms() -> None:
    stem = "The player aimed a gun 5 meters away"
    result = policy_check(stem)
    assert result.status != "pass"
    assert "forbidden_term" in result.issues


def test_cso_requires_units() -> None:
    stem = "A triangle has sides a and b"  # no units
    result = policy_check(stem)
    assert result.status != "pass"
    assert "missing_units" in result.issues
