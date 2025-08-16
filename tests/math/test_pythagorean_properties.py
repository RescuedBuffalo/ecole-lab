from math import isclose

from typing import cast

from hypothesis import given, strategies as st

from src.app.math.skills.pythagorean import generate_problem


@given(st.integers(min_value=1, max_value=2))
def test_d1_d2_triples(diff: int) -> None:
    spec = generate_problem("pythagorean.find_c", diff)
    a = float(cast(float, spec.vars["a"]))
    b = float(cast(float, spec.vars["b"]))
    c = float(cast(float, spec.vars["c"]))
    assert isclose(c**2, a**2 + b**2)
    assert float(c).is_integer()


@given(st.just(3))
def test_d3_non_integer_c(_: int) -> None:
    spec = generate_problem("pythagorean.find_c", 3)
    c = float(cast(float, spec.vars["c"]))
    assert not c.is_integer()
    a = float(cast(float, spec.vars["a"]))
    b = float(cast(float, spec.vars["b"]))
    from math import sqrt

    assert isclose(c, round(sqrt(a * a + b * b), 2))


def test_d4_find_leg() -> None:
    spec = generate_problem("pythagorean.find_leg", 4)
    a = float(cast(float, spec.vars["a"]))
    b = float(cast(float, spec.vars["b"]))
    c = float(cast(float, spec.vars["c"]))
    assert c > a
    assert c > b
    assert isclose(b**2 + a**2, c**2, rel_tol=1e-2)


@given(st.integers(min_value=1, max_value=3))
def test_swap_legs_invariance(diff: int) -> None:
    spec = generate_problem("pythagorean.find_c", diff)
    a = float(cast(float, spec.vars["a"]))
    b = float(cast(float, spec.vars["b"]))
    c = float(cast(float, spec.vars["c"]))
    assert isclose(c**2, a**2 + b**2, rel_tol=1e-2)
    # swapping legs should not change solution
    assert isclose(c**2, b**2 + a**2, rel_tol=1e-2)


@given(st.integers(min_value=1, max_value=2), st.integers(min_value=2, max_value=5))
def test_scaling_property(diff: int, k: int) -> None:
    spec = generate_problem("pythagorean.find_c", diff)
    a = float(cast(float, spec.vars["a"]))
    b = float(cast(float, spec.vars["b"]))
    c = float(cast(float, spec.vars["c"]))
    assert isclose((a * k) ** 2 + (b * k) ** 2, (c * k) ** 2)
