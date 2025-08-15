from src.app.math.teacher_math import evaluate_math_item
from src.app.math.cso_math import policy_check


def test_teacher_flags_long() -> None:
    stem = "One. Two. Three."
    res = evaluate_math_item(stem, "", "7-9")
    assert res.status == "needs_fix"


def test_cso_flags_weapon() -> None:
    stem = "A gun is 3 meters away forming a right angle."
    res = policy_check(stem)
    assert res.status == "needs_fix"
