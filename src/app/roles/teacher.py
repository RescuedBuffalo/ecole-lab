from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ..schemas import Draft, GateResult, Issue


@dataclass
class Teacher:
    constitution_path: Path

    def __post_init__(self) -> None:
        with self.constitution_path.open("r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f)["rules"]

    def score(self, text: str) -> dict[str, Any]:
        scores: dict[str, Any] = {}
        lower = text.lower()
        scores["learning_goal_present"] = 1 if "learn" in lower else 0
        scores["cognitive_progression"] = (
            0.7 if all(k in lower for k in ["remember", "understand", "apply"]) else 0.0
        )
        scores["retrieval_presence"] = lower.count("?")
        scores["reading_level_max_grade"] = 8  # pretend
        scores["udl_accessibility"] = (
            0.7 if "example" in lower or "recap" in lower else 0.0
        )
        scores["claims_softened_or_cited"] = (
            1 if ("may" in lower or "might" in lower or "http" in lower) else 0
        )
        return scores

    def review(self, draft: Draft) -> GateResult:
        scores = self.score(draft.text)
        issues: list[Issue] = []
        for rule in self.rules:
            key = rule["key"]
            val = scores.get(key, 0)
            if rule.get("required") and not val:
                issues.append(Issue(severity="high", code=key, message="missing"))
            if "min" in rule and val < rule["min"]:
                issues.append(Issue(severity="med", code=key, message="below min"))
            if "max" in rule and val > rule["max"]:
                issues.append(Issue(severity="med", code=key, message="above max"))
        status = "pass" if not issues else "needs_fix"
        return GateResult(status=status, issues=issues, teacher_scores=scores)
