from __future__ import annotations

import asyncio
import yaml  # type: ignore[import-untyped]

from ..db import async_session_maker
from ..models import Play, Workstream


def load_plays() -> list[dict]:
    with open("src/app/playbook/plays.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main() -> None:
    plays = load_plays()
    async with async_session_maker() as session:
        for p in plays:
            session.add(
                Play(
                    id=p["id"],
                    workstream=Workstream(p["workstream"]),
                    params=p.get("params", {}),
                )
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
