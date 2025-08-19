from __future__ import annotations

import random
from typing import List, Tuple

from .invariance import check_invariance
from .templater import render_context
from .schemas import ContextedItem, ProblemSpec


def build_pairs(
    specs: List[ProblemSpec], motif: str
) -> List[Tuple[ContextedItem, ContextedItem]]:
    pairs: List[Tuple[ContextedItem, ContextedItem]] = []
    for spec in specs:
        personalized = render_context(None, spec, motif, "meters")
        if not check_invariance(spec, personalized.stem):
            personalized = render_context("neutral_v1", spec, motif, "meters")
        neutral = render_context("neutral_v1", spec, motif, "meters")
        items = [personalized, neutral]
        random.shuffle(items)
        pairs.append((items[0], items[1]))
    return pairs
