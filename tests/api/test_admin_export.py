import asyncio
from sqlalchemy import select

from httpx import AsyncClient
from src.app.db import async_session_maker
from src.app.models import Attempt


def test_admin_export_contains_expected_fields(app):
    async def run() -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            pid = (
                await client.post(
                    "/math/participants",
                    json={"age_band": "7-9", "interests": ["Sports"]},
                )
            ).json()["participant_id"]
            sid = (
                await client.post(
                    "/math/sessions",
                    json={
                        "participant_id": pid,
                        "skill": "pythagorean.find_c",
                        "n_pairs": 1,
                    },
                )
            ).json()["session_id"]

            data = (await client.get(f"/math/sessions/{sid}/next")).json()
            await client.post(
                "/math/attempts",
                json={
                    "item_id": data["item_id"],
                    "answer_submitted": data["bindings"]["c"],
                },
            )

            async with async_session_maker() as db:
                res = await db.execute(select(Attempt))
                attempt = res.scalars().first()
                assert attempt is not None
                for field in [
                    "answer_submitted",
                    "first_try_correct",
                    "hints_used",
                    "retries",
                    "time_to_first_try_ms",
                ]:
                    assert hasattr(attempt, field)
                assert not hasattr(attempt, "email")

    asyncio.run(run())
