from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AttemptLog, Play


@dataclass
class Analyst:
    reward_path: Path

    def __post_init__(self) -> None:
        self.weights = yaml.safe_load(self.reward_path.read_text())

    def simulate_metrics(self, attempt: AttemptLog) -> None:
        seed = int(attempt.id.int % (2**32))
        random.seed(seed)
        attempt.metrics_1h = {"value": random.random()}
        attempt.metrics_24h = {"value": random.random()}
        attempt.metrics_72h = {"value": random.random()}

    def compute_reward(self, workstream: str, metrics: dict[str, float]) -> float:
        weights = self.weights.get(workstream, {})
        reward = 0.0
        for k, w in weights.items():
            if k.startswith("penalty"):
                continue
            reward += metrics.get(k, 0) * w
        return reward

    async def process(self, session: AsyncSession) -> None:
        result = await session.execute(
            select(AttemptLog).where(AttemptLog.reward_R.is_(None))
        )
        attempts = result.scalars().all()
        for attempt in attempts:
            self.simulate_metrics(attempt)
            metrics = dict(attempt.metrics_72h or {})
            attempt.reward_R = self.compute_reward(attempt.workstream.value, metrics)
            play = await session.get(Play, attempt.play_id)
            if play:
                params = play.params or {}
                params["reward_sum"] = params.get("reward_sum", 0) + float(
                    attempt.reward_R
                )
                params["n"] = params.get("n", 0) + 1
                play.params = params
        await session.commit()
