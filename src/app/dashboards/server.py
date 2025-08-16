from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_session
from ..models import AttemptLog


router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(AttemptLog).order_by(AttemptLog.timestamp.desc()).limit(50)
    )
    attempts = result.scalars().all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "attempts": attempts}
    )


@router.get("/attempt/{attempt_id}", response_class=HTMLResponse)
async def attempt_detail(
    attempt_id: str, request: Request, session: AsyncSession = Depends(get_session)
):
    attempt = await session.get(AttemptLog, attempt_id)
    return templates.TemplateResponse(
        "attempt.html", {"request": request, "attempt": attempt}
    )


@router.get("/m/welcome", response_class=HTMLResponse)
async def mobile_welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("mobile_welcome.html", {"request": request})


@router.get("/m/session/{session_id}", response_class=HTMLResponse)
async def mobile_session(session_id: str, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "mobile_session.html", {"request": request, "session_id": session_id}
    )
