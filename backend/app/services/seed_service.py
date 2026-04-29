from sqlalchemy.orm import Session as OrmSession

from app.models import Session, User
from app.services.memory_manager import memory_manager
from app.services.profile_service import get_or_create_profile
from app.utils.security import hash_password


DEMO_EMAIL = "demo@memorytutor.com"
DEMO_PASSWORD = "demo1234"


def seed_demo_data(db: OrmSession) -> User:
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if not user:
        user = User(
            name="Demo Student",
            email=DEMO_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            role="student",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    profile = get_or_create_profile(db, user.id)
    profile.preferences_json = {
        "explanation_style": "step-by-step",
        "response_length": "medium",
        "tone": "encouraging",
    }
    profile.goals_json = ["Improve algebra confidence"]
    profile.mastery_json = {"basic derivatives": "improving"}
    profile.misconceptions_json = ["Student struggles with fractions"]
    profile.progress_summary = "Student has improved in basic derivatives and should keep practicing algebra with fractions."
    db.commit()

    session = (
        db.query(Session)
        .filter(Session.user_id == user.id, Session.title == "Demo Algebra Session")
        .first()
    )
    if not session:
        session = Session(user_id=user.id, topic="algebra", title="Demo Algebra Session")
        db.add(session)
        db.commit()
        db.refresh(session)

    seeds = [
        ("Student prefers step-by-step explanations", "preference", "general", 5, 0.95),
        ("Student struggles with fractions", "misconception", "algebra", 5, 0.9),
        ("Student wants to improve algebra", "goal", "algebra", 4, 0.85),
        ("Student has improved in basic derivatives", "progress", "calculus", 4, 0.8),
    ]
    for text, memory_type, topic, importance, confidence in seeds:
        exists = (
            db.query(Session)
            .filter(Session.user_id == user.id, Session.id == session.id)
            .first()
        )
        if exists:
            memory_manager.store_memory(
                db,
                user.id,
                session.id,
                {
                    "memory_text": text,
                    "memory_type": memory_type,
                    "topic_tag": topic,
                    "importance_score": importance,
                    "confidence_score": confidence,
                },
            )
    return user
