from __future__ import annotations

import asyncio

from ..db import async_session_maker
from ..models import AttemptLog, Play, Workstream, CSOStatus, ShipAction


async def main() -> None:
    async with async_session_maker() as session:
        play = await session.get(Play, "x_hot_take_v1")
        if play:
            attempt = AttemptLog(
                workstream=Workstream.x_post,
                play_id=play.id,
                context={},
                cso_status=CSOStatus.pass_,
                ship_action=ShipAction.publish,
                reward_R=1.0,
            )
            session.add(attempt)
            play.params["reward_sum"] = play.params.get("reward_sum", 0) + 1
            play.params["n"] = play.params.get("n", 0) + 1
            await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
