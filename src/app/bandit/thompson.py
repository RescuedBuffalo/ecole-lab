from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict


@dataclass
class ArmState:
    reward_sum: float = 0.0
    n: int = 0

    @property
    def mean(self) -> float:
        return self.reward_sum / self.n if self.n else 0.0


@dataclass
class ThompsonBandit:
    arms: Dict[str, ArmState] = field(default_factory=dict)
    exploration: float = 0.15

    def sample(self) -> str:
        if not self.arms:
            raise ValueError("no arms")
        if random.random() < self.exploration:
            return random.choice(list(self.arms.keys()))
        samples: Dict[str, float] = {}
        for arm_id, state in self.arms.items():
            sigma = 1 / (state.n + 1) ** 0.5
            samples[arm_id] = random.normalvariate(state.mean, sigma)
        return max(samples, key=lambda k: samples[k])

    def update(self, arm_id: str, reward: float) -> None:
        state = self.arms.setdefault(arm_id, ArmState())
        state.reward_sum += reward
        state.n += 1
