import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import select, func

from src.app.main import app
from src.app.db import Base, engine, async_session_maker
from src.app.models import Attempt, Session as SessionModel


async def setup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(setup_db())


def test_math_end_to_end() -> None:
    client = TestClient(app)
    resp = client.post("/math/participants", json={"interests": ["Sports"]})
    participant_id = resp.json()["participant_id"]
    resp = client.post(
        "/math/sessions",
        json={
            "participant_id": participant_id,
            "skill": "pythagorean.find_c",
            "n_pairs": 1,
            "motif": "Sports",
        },
    )
    session_id = resp.json()["session_id"]
    for _ in range(2):
        item_resp = client.get(f"/math/sessions/{session_id}/next")
        item = item_resp.json()
        answer = float(item["bindings"]["c"])
        client.post(
            "/math/attempts",
            json={
                "item_id": item["item_id"],
                "answer_submitted": answer,
                "hints_used": 0,
                "retries": 0,
            },
        )
    final = client.get(f"/math/sessions/{session_id}/next")
    assert final.json()["item"] is None

    async def check_db() -> None:
        async with async_session_maker() as db:
            count = await db.scalar(select(func.count()).select_from(Attempt))
            sess = await db.get(SessionModel, session_id)
            assert count == 2
            assert sess.completed_at is not None

    asyncio.run(check_db())
