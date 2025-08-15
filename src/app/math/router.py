from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_session
from ..models import Attempt, Item, Participant, Session
from .pairing import build_pairs
from .schemas import AttemptIn, ProblemSpec
from .skills.pythagorean import generate_problem
from typing import cast, Literal

router = APIRouter()


@router.post("/participants")
async def create_participant(
    payload: dict[str, Any], session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    participant_id = uuid.uuid4().hex
    participant = Participant(
        participant_id=participant_id,
        age_band=payload.get("age_band"),
        interests=payload.get("interests"),
    )
    session.add(participant)
    await session.commit()
    return {"participant_id": participant_id}


@router.post("/sessions")
async def create_session(
    payload: dict[str, Any], session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    participant_id: str = payload["participant_id"]
    skill = payload.get("skill", "pythagorean.find_c")
    skill_literal = cast(
        Literal["pythagorean.find_c", "pythagorean.find_leg"], skill
    )
    n_pairs: int = payload.get("n_pairs", 5)
    motif: str = payload.get("motif", "neutral")
    difficulty_mix: List[int] | None = payload.get("difficulty_mix")
    if difficulty_mix is None:
        difficulty_mix = [1, 2, 3, 1, 2][:n_pairs]
    specs: List[ProblemSpec] = []
    for diff in difficulty_mix:
        specs.append(generate_problem(skill_literal, diff))
    pairs = build_pairs(specs, motif)
    session_id = uuid.uuid4().hex
    session_obj = Session(
        session_id=session_id, participant_id=participant_id, skill=skill
    )
    session.add(session_obj)
    for spec, pair in zip(specs, pairs):
        for item in pair:
            item_db = Item(
                item_id=item.item_id,
                session_id=session_id,
                problem_spec=spec.model_dump(),
                context_id=item.context_id,
                variant=item.variant,
                motif=motif,
            )
            session.add(item_db)
    await session.commit()
    return {"session_id": session_id}


async def _next_item(session_id: str, session: AsyncSession) -> Item | None:
    result = await session.execute(
        select(Item).where(Item.session_id == session_id).order_by(Item.created_at)
    )
    items = result.scalars().all()
    for item in items:
        res = await session.execute(
            select(Attempt).where(Attempt.item_id == item.item_id)
        )
        if res.scalars().first() is None:
            return item
    sess = await session.get(Session, session_id)
    if sess and not sess.completed_at:
        sess.completed_at = datetime.utcnow()
        await session.commit()
    return None


@router.get("/sessions/{session_id}/next")
async def get_next_item(session_id: str, session: AsyncSession = Depends(get_session)):
    item = await _next_item(session_id, session)
    if item is None:
        return {"item": None}
    spec = ProblemSpec(**item.problem_spec)
    from .templater import render_context

    units = str(spec.vars.get("units", "meters"))
    ctx_item = render_context(item.context_id, spec, item.motif or "", units)
    payload = ctx_item.model_dump()
    payload["item_id"] = item.item_id
    return payload


@router.post("/attempts")
async def log_attempt(
    attempt: AttemptIn, session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    item = await session.get(Item, attempt.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    spec = ProblemSpec(**item.problem_spec)
    correct = abs(attempt.answer_submitted - float(spec.solution["answer"])) < 1e-2
    attempt_db = Attempt(
        attempt_id=uuid.uuid4().hex,
        item_id=item.item_id,
        submitted_at=datetime.utcnow(),
        answer_submitted=attempt.answer_submitted,
        first_try_correct=correct and attempt.retries == 0,
        time_to_first_try_ms=0,
        hints_used=attempt.hints_used,
        retries=attempt.retries,
    )
    session.add(attempt_db)
    await session.commit()
    next_item = await _next_item(item.session_id, session)
    next_url = f"/math/sessions/{item.session_id}/next" if next_item else None
    return {"correct": correct, "next_item": next_url}


@router.post("/sessions/{session_id}/post_quiz")
async def post_quiz(
    session_id: str,
    payload: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    sess = await session.get(Session, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    sess.post_quiz = payload
    await session.commit()
    return {"status": "stored"}
