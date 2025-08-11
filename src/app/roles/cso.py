from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ..schemas import Draft, GateResult, Issue


@dataclass
class CSO:
    policy_dir: Path

    def load_policies(self, workstream: str) -> dict[str, Any]:
        common = yaml.safe_load((self.policy_dir / "common.yaml").read_text())
        specific_path = self.policy_dir / f"{workstream}.yaml"
        specific = {}
        if specific_path.exists():
            specific = yaml.safe_load(specific_path.read_text())
        merged = {**common, **specific}
        return merged

    def review(self, workstream: str, draft: Draft) -> GateResult:
        policies = self.load_policies(workstream)
        text = draft.text
        issues: list[Issue] = []
        for pattern in policies.get("forbidden", []):
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(Issue(severity="high", code="forbidden", message=pattern))
        for pattern in policies.get("pii", []):
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(Issue(severity="high", code="pii", message=pattern))
        auto_fixes: list[str] = []
        if "affiliate" in text.lower() and "affiliate" not in " ".join(
            draft.metadata.get("disclosures", [])
        ):
            disclosure = "This may contain affiliate links."
            draft.metadata.setdefault("disclosures", []).append(disclosure)
            auto_fixes.append("affiliate_disclosure")
        status = "pass" if not issues else "needs_fix"
        return GateResult(status=status, issues=issues, auto_fixes_applied=auto_fixes)
