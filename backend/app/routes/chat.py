from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import Message, Session, User
from app.routes.deps import get_current_user
from app.schemas.chat import ChatResponse, MessageCreate, MessageOut, SessionCreate, SessionDetail, SessionOut
from app.schemas.memory import RetrievedMemory
from app.services.memory_manager import _token_count, memory_manager
from app.services.profile_service import get_or_create_profile
from app.services.tutor_agent import tutor_agent


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=SessionOut)
def create_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    session = Session(
        user_id=current_user.id,
        topic=payload.topic or "general",
        title=payload.title or f"{payload.topic or 'Tutoring'} Session",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(current_user: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    return (
        db.query(Session)
        .filter(Session.user_id == current_user.id)
        .order_by(Session.started_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    session = _owned_session(db, current_user.id, session_id)
    return session


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
def send_message(
    session_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    session = _owned_session(db, current_user.id, session_id)
    if session.status == "ended":
        raise HTTPException(status_code=400, detail="Session has already ended")

    user_message = Message(
        session_id=session.id,
        user_id=current_user.id,
        sender_type="student",
        message_text=payload.message_text,
        token_count=_token_count(payload.message_text),
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    profile = get_or_create_profile(db, current_user.id)
    retrieved = []
    mode = payload.mode
    if mode == "hybrid_memory":
        retrieved = memory_manager.retrieve_memories(db, current_user.id, payload.message_text, session.topic, top_k=5)
    elif mode == "naive_rag":
        prior_messages = (
            db.query(Message)
            .filter(Message.session_id == session.id, Message.id != user_message.id)
            .order_by(Message.created_at.desc())
            .limit(30)
            .all()
        )
        retrieved = tutor_agent.raw_prior_message_memories(prior_messages, payload.message_text)

    response_text = tutor_agent.generate_response(
        current_user,
        session,
        payload.message_text,
        retrieved,
        profile,
        mode,
    )
    tutor_message = Message(
        session_id=session.id,
        user_id=current_user.id,
        sender_type="tutor",
        message_text=response_text,
        token_count=_token_count(response_text),
    )
    db.add(tutor_message)
    db.commit()
    db.refresh(tutor_message)

    facts = memory_manager.extract_facts(payload.message_text, response_text, session.topic)
    stored = [
        memory_manager.store_memory(db, current_user.id, session.id, fact, source_message_id=user_message.id)
        for fact in facts
    ]
    profile = get_or_create_profile(db, current_user.id)

    rendered_retrieved: list[RetrievedMemory] = []
    if mode == "hybrid_memory":
        for memory, score in retrieved:
            data = RetrievedMemory.model_validate(memory)
            data.relevance_score = score
            rendered_retrieved.append(data)
    elif mode == "naive_rag":
        rendered_retrieved = []

    return ChatResponse(
        session=SessionOut.model_validate(session),
        user_message=MessageOut.model_validate(user_message),
        tutor_message=MessageOut.model_validate(tutor_message),
        response_text=response_text,
        retrieved_memories=rendered_retrieved,
        stored_memories=stored,
        profile=profile,
        mode=mode,
        metadata={"facts_extracted": len(facts), "raw_prior_messages_used": len(retrieved) if mode == "naive_rag" else 0},
    )


@router.patch("/sessions/{session_id}/end", response_model=SessionOut)
def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    session = _owned_session(db, current_user.id, session_id)
    session.status = "ended"
    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def _owned_session(db: OrmSession, user_id: int, session_id: int) -> Session:
    session = db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

