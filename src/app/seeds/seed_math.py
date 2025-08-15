from __future__ import annotations

import asyncio
import uuid

from ..db import async_session_maker
from ..models import Item, Participant, Session
from ..math.pairing import build_pairs
from ..math.skills.pythagorean import generate_problem


async def main() -> None:
    async with async_session_maker() as session:
        participant = await session.get(Participant, "P-DEMO")
        if not participant:
            participant = Participant(
                participant_id="P-DEMO", interests=["Sports", "Games"]
            )
            session.add(participant)
            await session.commit()
        specs = [generate_problem("pythagorean.find_c", d) for d in [1, 2, 3, 1, 2]]
        pairs = build_pairs(specs, "Sports")
        session_id = uuid.uuid4().hex
        session_obj = Session(
            session_id=session_id,
            participant_id=participant.participant_id,
            skill="pythagorean.find_c",
        )
        session.add(session_obj)
        for spec, pair in zip(specs, pairs):
            for item in pair:
                session.add(
                    Item(
                        item_id=item.item_id,
                        session_id=session_id,
                        problem_spec=spec.model_dump(),
                        context_id=item.context_id,
                        variant=item.variant,
                        motif="Sports",
                    )
                )
        await session.commit()
        print(f"Session URL: http://localhost:8000/m/session/{session_id}")


if __name__ == "__main__":
    asyncio.run(main())
