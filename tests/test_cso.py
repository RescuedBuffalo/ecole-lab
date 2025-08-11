from pathlib import Path

from src.app.roles.cso import CSO
from src.app.schemas import Draft

POLICY_DIR = Path("src/app/playbook/policies")


def test_cso_flags_pii_and_forbidden():
    cso = CSO(POLICY_DIR)
    draft = Draft(outline=[], text="Email me at test@example.com for a guarantee!")
    res = cso.review("newsletter", draft)
    assert res.status != "pass"


def test_cso_auto_disclosure():
    cso = CSO(POLICY_DIR)
    draft = Draft(
        outline=[], text="Check this affiliate link", metadata={"disclosures": []}
    )
    res = cso.review("newsletter", draft)
    assert "affiliate_disclosure" in res.auto_fixes_applied
    assert any("affiliate" in d.lower() for d in draft.metadata["disclosures"])
