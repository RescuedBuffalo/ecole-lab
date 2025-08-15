from src.app.math.pairing import build_pairs
from src.app.math.skills.pythagorean import generate_problem


def test_math_pairing() -> None:
    specs = [generate_problem("pythagorean.find_c", 1) for _ in range(5)]
    pairs = build_pairs(specs, "Sports")
    assert len(pairs) == 5
    for a, b in pairs:
        assert a.bindings == b.bindings
        assert a.variant != b.variant
