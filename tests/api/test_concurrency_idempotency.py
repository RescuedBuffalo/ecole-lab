import asyncio

from sqlalchemy import select

from httpx import AsyncClient
from src.app.db import async_session_maker
from src.app.models import Attempt


async def create_basic_session(client: AsyncClient) -> str:
    pid = (
        await client.post(
            "/math/participants", json={"age_band": "7-9", "interests": []}
        )
    ).json()["participant_id"]
    sid = (
        await client.post(
            "/math/sessions",
            json={"participant_id": pid, "skill": "pythagorean.find_c", "n_pairs": 1},
        )
    ).json()["session_id"]
    return sid


def test_concurrent_next_calls(app):
    async def run() -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            sid = await create_basic_session(client)

            async def fetch_next():
                return (await client.get(f"/math/sessions/{sid}/next")).json()

            first, second = await asyncio.gather(fetch_next(), fetch_next())
            ids = [first.get("item_id"), second.get("item_id")]
            non_null = [i for i in ids if i]
            assert non_null

            item_id = first.get("item_id") or second.get("item_id")
            ans = first.get("bindings", {}).get("c") or second.get("bindings", {}).get(
                "c"
            )
            await client.post(
                "/math/attempts", json={"item_id": item_id, "answer_submitted": ans}
            )
            resp2 = await client.post(
                "/math/attempts", json={"item_id": item_id, "answer_submitted": ans}
            )
            assert resp2.status_code in (200, 409)

            async with async_session_maker() as db:
                res = await db.execute(
                    select(Attempt).where(
                        Attempt.item_id == item_id,
                        Attempt.answer_submitted.isnot(None),
                    )
                )
                attempts = res.scalars().all()
                assert len(attempts) >= 1

    asyncio.run(run())
