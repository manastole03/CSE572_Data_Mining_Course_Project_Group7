from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import EvaluationLog, MemoryEntry, Message, Session, User
from app.routes.deps import get_current_user
from app.schemas.admin import SystemStats
from app.services.seed_service import seed_demo_data
from app.services.vector_store import vector_store


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/system-stats", response_model=SystemStats)
def system_stats(_: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "sessions": db.query(func.count(Session.id)).scalar() or 0,
        "messages": db.query(func.count(Message.id)).scalar() or 0,
        "active_memories": db.query(func.count(MemoryEntry.id)).filter(MemoryEntry.status == "active").scalar() or 0,
        "deleted_memories": db.query(func.count(MemoryEntry.id)).filter(MemoryEntry.status == "deleted").scalar() or 0,
        "evaluation_runs": db.query(func.count(distinct(EvaluationLog.run_id))).scalar() or 0,
        "vector_store_available": vector_store.available,
    }


@router.post("/seed-demo")
def seed_demo(_: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    user = seed_demo_data(db)
    return {"ok": True, "demo_user_id": user.id, "email": user.email}

