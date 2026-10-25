"""Pydantic request/response models — the API contract, and auto-generated docs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class LogCreate(BaseModel):
    profile: str = Field("me", max_length=60)
    log_date: str = Field(..., description="ISO date, YYYY-MM-DD")
    is_period_start: bool = False
    flow: str = Field("none", pattern="^(none|spotting|light|medium|heavy|very_heavy)$")
    pain: int = Field(0, ge=0, le=10, description="0 = none, 10 = worst imaginable")
    symptoms: list[str] = Field(default_factory=list)
    notes: str = Field("", max_length=1000)


class LogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile: str
    log_date: str
    cycle_day: int | None = None
    is_period_start: bool = False
    flow: str
    pain: int
    symptoms: list[str] = Field(default_factory=list)
    notes: str = ""


class InsightsResponse(BaseModel):
    """Deliberately open: the frontend renders whatever the engine produces."""
    profile: str
    generated_at: str
    disclaimer: str
    cycle_stats: dict[str, Any]
    signals: list[dict[str, Any]]
    urgency: dict[str, str]
    report_markdown: str


class ScenarioRequest(BaseModel):
    scenario: str = Field("pcos", pattern="^(pcos|endometriosis|anaemia|healthy)$")
    profile: str = "me"
