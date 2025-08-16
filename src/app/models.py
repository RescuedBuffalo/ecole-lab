from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Boolean,
    Float,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Workstream(str, Enum):
    x_post = "x_post"
    x_thread = "x_thread"
    newsletter = "newsletter"
    medium = "medium"
    tpt = "tpt"


class CSOStatus(str, Enum):
    pass_ = "pass"
    needs_fix = "needs_fix"
    fail = "fail"


class ShipAction(str, Enum):
    publish = "publish"
    revise = "revise"
    discard = "discard"
    ab_test = "ab_test"


class AttemptLog(Base):
    __tablename__ = "attempt_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    workstream: Mapped[Workstream] = mapped_column(SAEnum(Workstream))
    play_id: Mapped[str] = mapped_column(ForeignKey("plays.id"))
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    draft_hash: Mapped[str] = mapped_column(String, default="")
    cost_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_assets: Mapped[float] = mapped_column(Numeric, default=0)
    cso_status: Mapped[CSOStatus] = mapped_column(
        SAEnum(CSOStatus), default=CSOStatus.pass_
    )
    cso_issues: Mapped[list[Any]] = mapped_column(JSON, default=list)
    teacher_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ship_action: Mapped[ShipAction] = mapped_column(
        SAEnum(ShipAction), default=ShipAction.revise
    )
    publisher_payload_path: Mapped[str | None] = mapped_column(String, nullable=True)
    metrics_1h: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metrics_24h: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metrics_72h: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    revenue: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    policy_events: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    reward_R: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    propensity: Mapped[float | None] = mapped_column(Numeric, nullable=True)

    play: Mapped["Play"] = relationship(back_populates="attempts")


class Play(Base):
    __tablename__ = "plays"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workstream: Mapped[Workstream] = mapped_column(SAEnum(Workstream))
    params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    attempts: Mapped[list[AttemptLog]] = relationship(back_populates="play")


class PolicyIncident(Base):
    __tablename__ = "policy_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attempt_logs.id")
    )
    code: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)

    attempt: Mapped[AttemptLog] = relationship()


class UserStub(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class Participant(Base):
    __tablename__ = "participants"

    participant_id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    age_band: Mapped[str | None] = mapped_column(String, nullable=True)
    interests: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    participant_id: Mapped[str] = mapped_column(
        String, ForeignKey("participants.participant_id")
    )
    skill: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    post_quiz: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Item(Base):
    __tablename__ = "items"

    item_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.session_id"))
    problem_spec: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    context_id: Mapped[str] = mapped_column(String, nullable=False)
    variant: Mapped[str] = mapped_column(String, nullable=False)
    motif: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Attempt(Base):
    __tablename__ = "attempts"

    attempt_id: Mapped[str] = mapped_column(String, primary_key=True)
    item_id: Mapped[str] = mapped_column(String, ForeignKey("items.item_id"))
    shown_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    answer_submitted: Mapped[float | None] = mapped_column(Float, nullable=True)
    first_try_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    time_to_first_try_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    retries: Mapped[int] = mapped_column(Integer, default=0)
