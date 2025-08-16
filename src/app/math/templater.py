from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Literal
import uuid

import yaml  # type: ignore[import-untyped]

from .schemas import ContextedItem, ProblemSpec

_TEMPLATE_PATH = Path(__file__).parent / "contexts" / "templates"

_MOTIF_MAP = {
    "Sports": "f1_turnin_v1",
    "Games": "esports_sightline_v1",
    "Music": "music_stage_v1",
    "Nature": "nature_trail_v1",
    "Space": "space_vectors_v1",
    "Cooking": "cooking_kitchen_v1",
    "Pets": "pets_backyard_v1",
}

_templates_cache: Dict[str, Dict] = {}


def _load_template(template_id: str) -> Dict:
    if template_id not in _templates_cache:
        with (_TEMPLATE_PATH / f"{template_id}.yaml").open("r", encoding="utf-8") as f:
            _templates_cache[template_id] = yaml.safe_load(f)
    return _templates_cache[template_id]


def render_context(
    template_id: str | None,
    spec: ProblemSpec,
    motif: str,
    units: str = "meters",
) -> ContextedItem:
    if template_id is None:
        template_id = _MOTIF_MAP.get(motif, "neutral_v1")
    template = _load_template(template_id)

    if units not in template.get("allowed_units", []):
        units = template.get("allowed_units", ["meters"])[0]

    bindings = {**spec.vars, "units": units}
    stem = template["stem"].format(**bindings)
    question = template["question"].format(**bindings)

    # validate sentence count
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", stem) if s.strip()]
    if len(sentences) > template.get("sentences_max", 2):
        raise ValueError("stem exceeds sentence limit")

    # validate placeholders
    placeholders = template.get("placeholders", [])
    for ph in placeholders:
        if ph not in bindings:
            raise ValueError(f"missing placeholder {ph}")

    variant: Literal["personalized", "neutral"] = (
        "neutral" if template_id == "neutral_v1" else "personalized"
    )

    return ContextedItem(
        item_id=uuid.uuid4().hex,
        context_id=template_id,
        variant=variant,
        stem=stem,
        question=question,
        bindings=bindings,
        skill=spec.skill,
        difficulty=spec.difficulty,
    )
