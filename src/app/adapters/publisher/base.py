from __future__ import annotations

import json
from pathlib import Path

from ...config import get_settings
from ...schemas import Draft


class BasePublisher:
    workstream: str

    def __init__(self) -> None:
        self.settings = get_settings()
        Path(self.settings.outbox_dir).mkdir(exist_ok=True)

    def publish(self, attempt_id: str, draft: Draft) -> str:
        out_dir = Path(self.settings.outbox_dir) / attempt_id
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = {"workstream": self.workstream, "draft": draft.dict()}
        path = out_dir / f"{self.workstream}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        body = draft.platform_packaging.get(self.workstream, {}).get("body_md")
        if body:
            (out_dir / f"{self.workstream}.md").write_text(body, encoding="utf-8")
        return str(path)
