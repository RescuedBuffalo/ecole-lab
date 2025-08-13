from __future__ import annotations

import hashlib

from .provider import LLMProvider


class MockLLM(LLMProvider):
    def generate(self, prompt: str, tone: str) -> str:
        seed = hashlib.md5((prompt + tone).encode()).hexdigest()[:8]
        return f"{prompt} | tone:{tone} | {seed}"
