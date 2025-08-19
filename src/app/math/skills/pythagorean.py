from __future__ import annotations

import math
import random
import uuid
from typing import Literal

from typing import Dict, Union

from ..schemas import ProblemSpec

# Predefined triples for easier difficulties
D1_TRIPLES = [(3, 4, 5), (6, 8, 10)]
D2_TRIPLES = [(9, 12, 15), (12, 16, 20)]

random_seed = 42
_rng = random.Random(random_seed)


def generate_problem(
    skill: Literal["pythagorean.find_c", "pythagorean.find_leg"],
    difficulty: int,
) -> ProblemSpec:
    """Generate a Pythagorean problem specification."""
    vars_: Dict[str, Union[int, float, str]]
    answer: float
    if skill == "pythagorean.find_c":
        if difficulty == 1:
            a_i, b_i, c_i = _rng.choice(D1_TRIPLES)
            a, b, c = float(a_i), float(b_i), float(c_i)
        elif difficulty == 2:
            a_i, b_i, c_i = _rng.choice(D2_TRIPLES)
            a, b, c = float(a_i), float(b_i), float(c_i)
        elif difficulty == 3:
            a = float(_rng.randint(5, 20))
            b = float(_rng.randint(5, 20))
            c = round(math.sqrt(a * a + b * b), 2)
        else:
            raise ValueError("difficulty 1-3 for find_c")
        vars_ = {"a": a, "b": b, "c": c}
        answer = float(c)
    elif skill == "pythagorean.find_leg":
        if difficulty != 4:
            raise ValueError("difficulty must be 4 for find_leg")
        a = float(_rng.randint(6, 15))
        b = round(_rng.uniform(4, 12), 2)
        c = round(math.sqrt(a * a + b * b), 2)
        vars_ = {"a": a, "b": b, "c": c}
        answer = float(b)
    else:
        raise ValueError("unknown skill")

    return ProblemSpec(
        id=uuid.uuid4().hex,
        skill=skill,
        difficulty=difficulty,
        vars=vars_,
        solution={"answer": answer},
    )
