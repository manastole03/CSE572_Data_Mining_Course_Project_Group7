from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.memory import MemoryOut, RetrievedMemory
from app.schemas.profile import ProfileOut


class SessionCreate(BaseModel):
    topic: str = "general"
    title: str | None = None


class SessionOut(BaseModel):
    id: int
    user_id: int
    topic: str
    title: str
    status: str
    started_at: datetime
    ended_at: datetime | None = None

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: int
    session_id: int
    user_id: int
    sender_type: str
    message_text: str
    token_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionDetail(SessionOut):
    messages: list[MessageOut] = []


class MessageCreate(BaseModel):
    message_text: str = Field(..., min_length=1)
    mode: str = "hybrid_memory"


class ChatResponse(BaseModel):
    session: SessionOut
    user_message: MessageOut
    tutor_message: MessageOut
    response_text: str
    retrieved_memories: list[RetrievedMemory] = []
    stored_memories: list[MemoryOut] = []
    profile: ProfileOut
    mode: str
    metadata: dict[str, Any] = {}

