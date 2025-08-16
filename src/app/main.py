from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .deps import get_session
from .models import AttemptLog, Play, Workstream
from .schemas import AttemptRead
from .llm.mock import MockLLM
from .roles.writer import Writer
from .roles.teacher import Teacher
from .roles.cso import CSO
from .roles.analyst import Analyst
from .roles.ceo import CEO
from .adapters.publisher.x_stub import XPublisher
from .adapters.publisher.newsletter_stub import NewsletterPublisher
from .adapters.publisher.medium_stub import MediumPublisher
from .adapters.publisher.tpt_stub import TPTPublisher
from .dashboards import server as dashboard
from .math.router import router as math_router
from .autodev.scaffolder import scaffold

app = FastAPI()
settings = get_settings()


@app.on_event("startup")
async def startup() -> None:
    Path(settings.outbox_dir).mkdir(exist_ok=True)


# Instantiate roles
mock_llm = MockLLM()
writer = Writer(mock_llm)
teacher = Teacher(Path("src/app/playbook/teaching_constitution.yaml"))
cso = CSO(Path("src/app/playbook/policies"))
publishers = {
    Workstream.x_post: XPublisher(),
    Workstream.newsletter: NewsletterPublisher(),
    Workstream.medium: MediumPublisher(),
    Workstream.tpt: TPTPublisher(),
    Workstream.x_thread: XPublisher(),
}
analyst = Analyst(Path("src/app/playbook/rewards.yaml"))
ceo = CEO(writer, teacher, cso, publishers)

app.include_router(dashboard.router)
app.include_router(math_router, prefix="/math", tags=["math"])


@app.post("/tasks", response_model=AttemptRead)
async def create_task(payload: dict, session: AsyncSession = Depends(get_session)):
    attempt = await ceo.run_task(session, payload)
    path = Path(settings.outbox_dir) / str(attempt.id) / "x_post.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")
    return AttemptRead.model_validate(attempt)


@app.get("/attempts", response_model=list[AttemptRead])
async def list_attempts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(AttemptLog).order_by(AttemptLog.timestamp.desc())
    )
    attempts = result.scalars().all()
    return [AttemptRead.model_validate(a) for a in attempts]


@app.get("/attempts/{attempt_id}", response_model=AttemptRead)
async def get_attempt(attempt_id: str, session: AsyncSession = Depends(get_session)):
    attempt = await session.get(AttemptLog, UUID(attempt_id))
    if not attempt:
        raise HTTPException(status_code=404, detail="not found")
    return AttemptRead.model_validate(attempt)


@app.post("/metrics/simulate")
async def simulate_metrics(session: AsyncSession = Depends(get_session)):
    await analyst.process(session)
    return {"status": "ok"}


@app.get("/plays")
async def get_plays(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Play).where(Play.active.is_(True)))
    plays = result.scalars().all()
    return [{"id": p.id, "workstream": p.workstream} for p in plays]


@app.post("/autodev/scaffold")
async def autodev_scaffold(spec: dict):
    path = scaffold(spec)
    return {"path": str(path)}
