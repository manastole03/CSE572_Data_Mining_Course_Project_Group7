from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import MemoryEntry, User
from app.routes.deps import get_current_user
from app.schemas.memory import MemoryCreate, MemoryOut, MemoryRetrieveRequest, MemoryUpdate, RetrievedMemory
from app.services.memory_manager import memory_manager


router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryOut])
def list_memories(
    search: str | None = None,
    memory_type: str | None = None,
    topic: str | None = None,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    query = db.query(MemoryEntry).filter(MemoryEntry.user_id == current_user.id, MemoryEntry.status == "active")
    if search:
        query = query.filter(MemoryEntry.memory_text.ilike(f"%{search}%"))
    if memory_type:
        query = query.filter(MemoryEntry.memory_type == memory_type)
    if topic:
        query = query.filter(MemoryEntry.topic_tag == topic)
    return query.order_by(MemoryEntry.updated_at.desc()).all()


@router.get("/{memory_id}", response_model=MemoryOut)
def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    return _owned_memory(db, current_user.id, memory_id)


@router.post("", response_model=MemoryOut)
def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    memory = memory_manager.store_memory(
        db,
        current_user.id,
        payload.session_id,
        payload.model_dump(),
    )
    return memory


@router.put("/{memory_id}", response_model=MemoryOut)
def update_memory(
    memory_id: int,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    memory = _owned_memory(db, current_user.id, memory_id)
    return memory_manager.update_memory(db, memory, payload)


@router.delete("/{memory_id}", response_model=MemoryOut)
def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    memory = _owned_memory(db, current_user.id, memory_id)
    return memory_manager.delete_memory(db, memory)


@router.post("/retrieve", response_model=list[RetrievedMemory])
def retrieve_memories(
    payload: MemoryRetrieveRequest,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    matches = memory_manager.retrieve_memories(db, current_user.id, payload.query, payload.topic, payload.top_k)
    output = []
    for memory, score in matches:
        item = RetrievedMemory.model_validate(memory)
        item.relevance_score = score
        output.append(item)
    return output


@router.post("/summarize", response_model=list[MemoryOut])
def summarize_memories(
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    return memory_manager.summarize_memories(db, current_user.id)


def _owned_memory(db: OrmSession, user_id: int, memory_id: int) -> MemoryEntry:
    memory = db.get(MemoryEntry, memory_id)
    if not memory or memory.user_id != user_id or memory.status != "active":
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

