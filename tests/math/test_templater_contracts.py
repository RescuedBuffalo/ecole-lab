from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

from src.app.math.templater import render_context, _TEMPLATE_PATH
from src.app.math.schemas import ProblemSpec


def _all_templates() -> list[Path]:
    return list(_TEMPLATE_PATH.glob("*.yaml"))


def test_templates_have_placeholders() -> None:
    for tpl_path in _all_templates():
        data = yaml.safe_load(tpl_path.read_text())
        assert set(["a", "b", "c", "units"]).issubset(set(data.get("placeholders", [])))


def test_stems_sentence_cap(sample_spec) -> None:
    for tpl_path in _all_templates():
        render_context(tpl_path.stem, sample_spec, "Sports", "meters")


def test_render_injects_numbers(sample_spec) -> None:
    ctx = render_context("neutral_v1", sample_spec, "neutral", "meters")
    a = str(int(float(sample_spec.vars["a"])))
    assert a in ctx.stem


def test_missing_placeholder_raises() -> None:
    spec = ProblemSpec(
        id="x",
        skill="pythagorean.find_c",
        difficulty=1,
        vars={"a": 3, "b": 4},
        solution={"answer": 5},
    )
    with pytest.raises(ValueError):
        render_context("neutral_v1", spec, "neutral", "meters")
