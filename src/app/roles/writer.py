from __future__ import annotations

from ..llm.provider import LLMProvider
from ..schemas import Draft, TaskSpec


class Writer:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def write(self, spec: TaskSpec) -> Draft:
        outline = ["hook", "point_1", "point_2", "cta"]
        base = f"{spec.topic} for {spec.audience}"
        raw = self.provider.generate(base, spec.tone)
        text = (
            f"{raw} learn to remember, understand and apply? "
            "Here is an example that may help you."
        )
        packaging = {
            "x_post": {"text": text[:280], "alt_text": None},
            "newsletter": {
                "subject_A": spec.topic,
                "subject_B": spec.topic + "!",
                "preheader": "",
                "body_md": text,
            },
            "medium": {"title": spec.topic, "body_md": text},
            "tpt": {"title": spec.topic, "description_md": text, "grades": ["9-12"]},
        }
        return Draft(outline=outline, text=text, platform_packaging=packaging)
