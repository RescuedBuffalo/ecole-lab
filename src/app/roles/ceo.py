from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..bandit.thompson import ThompsonBandit, ArmState
from ..models import AttemptLog, Play, Workstream, CSOStatus, ShipAction
from ..schemas import TaskSpec
from ..adapters.publisher.base import BasePublisher
from ..roles.writer import Writer
from ..roles.teacher import Teacher
from ..roles.cso import CSO


@dataclass
class CEO:
    writer: Writer
    teacher: Teacher
    cso: CSO
    publishers: Dict[Workstream, BasePublisher]

    async def choose_play(self, session: AsyncSession, workstream: Workstream) -> Play:
        result = await session.execute(
            select(Play).where(Play.workstream == workstream, Play.active.is_(True))
        )
        plays = result.scalars().all()
        bandit = ThompsonBandit(
            {
                p.id: ArmState(
                    reward_sum=p.params.get("reward_sum", 0),
                    n=p.params.get("n", 0),
                )
                for p in plays
            }
        )
        play_id = bandit.sample()
        return next(p for p in plays if p.id == play_id)

    async def run_task(self, session: AsyncSession, payload: dict) -> AttemptLog:
        workstream = Workstream(payload.get("workstream", "x_post"))
        play = await self.choose_play(session, workstream)
        spec = TaskSpec(
            objective=payload.get("objective", "subs"),
            workstream=workstream,
            topic=payload["topic"],
            audience=payload["audience"],
            tone=payload.get("tone", ""),
            play_id=play.id,
        )
        draft = self.writer.write(spec)
        teacher_res = self.teacher.review(draft)
        cso_res = self.cso.review(workstream.value, draft)
        ship = (
            ShipAction.publish
            if teacher_res.status == "pass" and cso_res.status == "pass"
            else ShipAction.revise
        )
        attempt = AttemptLog(
            workstream=workstream,
            play_id=play.id,
            context=payload,
            cso_status=CSOStatus(cso_res.status),
            cso_issues=[i.dict() for i in cso_res.issues],
            teacher_scores=teacher_res.teacher_scores,
            ship_action=ship,
        )
        session.add(attempt)
        await session.flush()
        if ship == ShipAction.publish:
            publisher = self.publishers[workstream]
            path = publisher.publish(str(attempt.id), draft)
            attempt.publisher_payload_path = path
        await session.commit()
        await session.refresh(attempt)
        return attempt
