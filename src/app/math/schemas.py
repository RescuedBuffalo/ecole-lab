from __future__ import annotations

from typing import Dict, Literal, Union

from pydantic import BaseModel, Field
from typing import Annotated

Difficulty = Annotated[int, Field(ge=1, le=4)]


class ProblemSpec(BaseModel):
    id: str
    skill: Literal["pythagorean.find_c", "pythagorean.find_leg"]
    difficulty: Difficulty
    vars: Dict[str, Union[int, float, str]]
    solution: Dict[str, Union[int, float, str]]


class ContextedItem(BaseModel):
    item_id: str
    context_id: str
    variant: Literal["personalized", "neutral"]
    stem: str
    question: str
    bindings: Dict[str, Union[int, float, str]]
    skill: str
    difficulty: int


class AttemptIn(BaseModel):
    item_id: str
    answer_submitted: float
    hints_used: int = 0
    retries: int = 0
