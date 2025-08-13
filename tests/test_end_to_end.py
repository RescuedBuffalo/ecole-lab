import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from src.app.main import app
from src.app.db import Base, engine, async_session_maker
from src.app.seeds.seed_plays import load_plays
from src.app.models import Play, Workstream


async def setup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    plays = load_plays()
    async with async_session_maker() as session:
        for p in plays:
            session.add(
                Play(id=p["id"], workstream=Workstream(p["workstream"]), params={})
            )
        await session.commit()


asyncio.run(setup_db())


def test_full_flow(tmp_path: Path):
    client = TestClient(app)
    payload = {
        "topic": "Active recall for exam week",
        "audience": "college students",
        "objective": "subs",
        "tone": "friendly, practical",
    }
    resp = client.post("/tasks", json=payload)
    assert resp.status_code == 200
    attempt_id = resp.json()["id"]
    out_file = Path("outbox") / attempt_id / "x_post.json"
    assert out_file.exists()
    resp2 = client.post("/metrics/simulate")
    assert resp2.status_code == 200
    resp3 = client.get(f"/attempts/{attempt_id}")
    assert resp3.json()["reward_R"] is not None
