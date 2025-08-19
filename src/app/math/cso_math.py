from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CSOResult:
    status: str
    issues: List[str]


def policy_check(stem: str) -> CSOResult:
    issues: List[str] = []
    lower = stem.lower()
    for term in ["gun", "weapon", "kill", "shoot"]:
        if term in lower:
            issues.append("forbidden_term")
    if "meter" not in lower and "foot" not in lower:
        issues.append("missing_units")

    status = "pass" if not issues else "needs_fix"
    return CSOResult(status=status, issues=issues)
