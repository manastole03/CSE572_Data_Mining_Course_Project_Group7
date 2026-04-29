from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


MEMORY_TYPES = {"misconception", "preference", "goal", "mastery", "progress", "summary", "other"}


class MemoryCreate(BaseModel):
    memory_text: str = Field(..., min_length=3)
    memory_type: str = "other"
    topic_tag: str = "general"
    importance_score: float = Field(3.0, ge=1, le=5)
    confidence_score: float = Field(0.7, ge=0, le=1)
    session_id: int | None = None


class MemoryUpdate(BaseModel):
    memory_text: str | None = None
    memory_type: str | None = None
    topic_tag: str | None = None
    importance_score: float | None = Field(default=None, ge=1, le=5)
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class MemoryOut(BaseModel):
    id: int
    user_id: int
    session_id: int | None = None
    memory_text: str
    memory_type: str
    topic_tag: str
    source_message_id: int | None = None
    importance_score: float
    confidence_score: float
    vector_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class MemoryRetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    topic: str | None = None
    top_k: int = Field(5, ge=1, le=20)


class RetrievedMemory(MemoryOut):
    relevance_score: float = 0.0

