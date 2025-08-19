from typing import List


import asyncio
from sqlalchemy import select

from httpx import AsyncClient
from src.app.db import async_session_maker
from src.app.models import Attempt, Item


async def _create_participant(client: AsyncClient):
    resp = await client.post(
        "/math/participants", json={"age_band": "7-9", "interests": ["Sports"]}
    )
    return resp.json()["participant_id"]


async def _create_session(client: AsyncClient, participant_id: str) -> str:
    resp = await client.post(
        "/math/sessions",
        json={
            "participant_id": participant_id,
            "skill": "pythagorean.find_c",
            "n_pairs": 5,
        },
    )
    return resp.json()["session_id"]


async def _consume_session(client: AsyncClient, session_id: str) -> List[str]:
    item_ids: List[str] = []
    for _ in range(10):
        data = (await client.get(f"/math/sessions/{session_id}/next")).json()
        if not data.get("item_id"):
            break
        item_ids.append(data["item_id"])
        ans = data["bindings"]["c"]
        await client.post(
            "/math/attempts", json={"item_id": data["item_id"], "answer_submitted": ans}
        )
    return item_ids


def test_full_session_flow(app):
    async def run() -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            pid = await _create_participant(client)
            sid = await _create_session(client, pid)
            async with async_session_maker() as db:
                res = await db.execute(select(Item).where(Item.session_id == sid))
                rows = res.scalars().all()
                # ensure each problem spec is represented in the session
                assert len(rows) > 0
            await _consume_session(client, sid)
            await client.post(f"/math/sessions/{sid}/post_quiz", json={"score": 4})

            async with async_session_maker() as db:
                res = await db.execute(
                    select(Attempt).join(Item).where(Item.session_id == sid)
                )
                attempts = res.scalars().all()
                assert len(attempts) == len(rows)
                assert all(a.first_try_correct for a in attempts)
                assert all(a.hints_used == 0 for a in attempts)
                assert all(a.retries == 0 for a in attempts)

    asyncio.run(run())
