from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict


@dataclass
class TeacherResult:
    status: str
    scores: Dict[str, float]


def evaluate_math_item(stem: str, question: str, grade_band: str) -> TeacherResult:
    text = stem.lower()
    cues = ["right angle", "straight-line"]
    relevance = sum(1 for cue in cues if cue in text)

    sentences = [s for s in stem.split(".") if s.strip()]
    words = re.findall(r"[A-Za-z]+", stem)
    avg_len = (sum(len(w) for w in words) / len(words)) if words else 0

    scores = {
        "context_relevance": float(relevance),
        "sentence_count": float(len(sentences)),
        "avg_word_len": avg_len,
    }
    status = "pass" if relevance >= 1 and len(sentences) <= 2 else "needs_fix"
    return TeacherResult(status=status, scores=scores)
