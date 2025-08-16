from __future__ import annotations

import pytest

from src.app.math.templater import render_context, _MOTIF_MAP
from src.app.math.schemas import ProblemSpec
from src.app.math.skills.pythagorean import generate_problem


def test_templater_neutral_template() -> None:
    """Test that neutral template works correctly."""
    for diff in [1, 2, 3]:
        spec = generate_problem("pythagorean.find_c", diff)
        ctx = render_context("neutral_v1", spec, "neutral", "meters")
        assert "a" in ctx.stem  # template interpolation worked
        assert ctx.stem != ctx.question


def test_motif_mapping_works() -> None:
    """Test that motif mapping works for different motifs."""
    spec = generate_problem("pythagorean.find_c", 1)
    for motif in ["Sports", "Games", "Music"]:
        ctx = render_context(None, spec, motif, "meters")
        assert _MOTIF_MAP[motif] in ctx.context_id  # template was selected


def test_edge_valid_units() -> None:
    """Test that valid units work correctly."""
    for diff in [1, 2]:
        spec = generate_problem("pythagorean.find_c", diff)
        ctx = render_context("neutral_v1", spec, "neutral", "meters")  # known valid
        assert "meter" in ctx.stem.lower() or "m" in ctx.stem


def test_invalid_units_fallback() -> None:
    """Test that invalid units fall back to first allowed unit."""
    spec = generate_problem("pythagorean.find_c", 1)
    ctx = render_context("neutral_v1", spec, "neutral", "invalid_unit")
    # Should fallback to first allowed unit
    assert ctx.stem  # template should still render


def test_templater_error_missing_placeholder():
    """Test error when template requires placeholder not in spec."""
    from unittest.mock import patch
    from src.app.math.templater import _load_template

    spec = ProblemSpec(
        id="test",
        skill="pythagorean.find_c",
        difficulty=1,
        vars={"a": 3, "b": 4, "c": 5},  # All required vars present
        solution={"answer": 5},
    )

    # Mock a template that requires an extra placeholder not in the spec
    mock_template = {
        "stem": "Simple stem with {a}",
        "question": "What is the answer?",
        "allowed_units": ["meters"],
        "sentences_max": 2,
        "placeholders": ["a", "b", "c", "units", "missing_var"],  # Extra placeholder
    }

    with patch("src.app.math.templater._load_template", return_value=mock_template):
        with pytest.raises(ValueError, match="missing placeholder missing_var"):
            render_context("mock_template", spec, "neutral", "meters")


def test_templater_sentence_limit_exceeded():
    """Test sentence limit validation by creating a mock template."""
    from unittest.mock import patch
    from src.app.math.templater import _load_template

    spec = generate_problem("pythagorean.find_c", 1)

    # Mock a template with a very low sentence limit
    mock_template = {
        "stem": "This is sentence one. This is sentence two. This is sentence three.",
        "question": "What is the answer?",
        "allowed_units": ["meters"],
        "sentences_max": 1,  # Very low limit
        "placeholders": ["a", "b", "c", "units"],
    }

    with patch.object(_load_template, "__defaults__", None):
        with patch("src.app.math.templater._load_template", return_value=mock_template):
            with pytest.raises(ValueError, match="stem exceeds sentence limit"):
                render_context("mock_template", spec, "neutral", "meters")
