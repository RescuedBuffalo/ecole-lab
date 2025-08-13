from __future__ import annotations
import uuid

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .models import Workstream, CSOStatus, ShipAction


class TaskSpec(BaseModel):
    objective: str
    workstream: Workstream
    topic: str
    audience: str
    tone: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    play_id: str
    budget: dict[str, Any] = Field(default_factory=dict)


class Draft(BaseModel):
    outline: List[str]
    text: str
    assets: List[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(
        default_factory=lambda: {
            "claims": [],
            "links": [],
            "disclosures": [],
        }
    )
    platform_packaging: dict[str, Any] = Field(default_factory=dict)


class Issue(BaseModel):
    severity: str
    code: str
    message: str
    suggest_fix: Optional[str] = None


class GateResult(BaseModel):
    status: str
    issues: List[Issue] = Field(default_factory=list)
    required_disclosures: List[str] = Field(default_factory=list)
    auto_fixes_applied: List[str] = Field(default_factory=list)
    teacher_scores: dict[str, Any] = Field(default_factory=dict)


class ShipDecision(BaseModel):
    action: ShipAction
    schedule_time: datetime | None = None
    ab: dict[str, Any] | None = None


class AttemptRead(BaseModel):
    id: uuid.UUID
    workstream: Workstream
    play_id: str
    cso_status: CSOStatus
    ship_action: ShipAction
    reward_R: float | None

    class Config:
        from_attributes = True
