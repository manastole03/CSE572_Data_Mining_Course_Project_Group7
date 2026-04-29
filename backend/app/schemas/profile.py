from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    preferences_json: dict[str, Any] | None = None
    goals_json: list[str] | None = None
    mastery_json: dict[str, Any] | None = None
    misconceptions_json: list[str] | None = None
    progress_summary: str | None = None


class ProfileOut(BaseModel):
    id: int
    user_id: int
    preferences_json: dict[str, Any]
    goals_json: list[str]
    mastery_json: dict[str, Any]
    misconceptions_json: list[str]
    progress_summary: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProgressOut(BaseModel):
    sessions_count: int
    messages_count: int
    memories_count: int
    weak_topics: list[str]
    mastered_topics: list[str]
    recent_progress_summary: str
    suggested_next_topic: str

