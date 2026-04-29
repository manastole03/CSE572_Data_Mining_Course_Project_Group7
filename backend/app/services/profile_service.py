from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession

from app.models import MemoryEntry, Message, Session, StudentProfile


DEFAULT_PREFERENCES = {
    "explanation_style": "step-by-step",
    "response_length": "medium",
    "tone": "encouraging",
}


def get_or_create_profile(db: OrmSession, user_id: int) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if profile:
        return profile
    profile = StudentProfile(
        user_id=user_id,
        preferences_json=DEFAULT_PREFERENCES.copy(),
        goals_json=[],
        mastery_json={},
        misconceptions_json=[],
        progress_summary="No progress summary yet.",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile_from_fact(db: OrmSession, user_id: int, fact: dict) -> StudentProfile:
    profile = get_or_create_profile(db, user_id)
    text = fact["memory_text"]
    topic = fact.get("topic_tag") or "general"
    kind = fact.get("memory_type") or "other"

    preferences = dict(profile.preferences_json or DEFAULT_PREFERENCES.copy())
    goals = list(profile.goals_json or [])
    mastery = dict(profile.mastery_json or {})
    misconceptions = list(profile.misconceptions_json or [])

    if kind == "preference":
        lower = text.lower()
        if "visual" in lower:
            preferences["explanation_style"] = "visual"
        if "step" in lower:
            preferences["explanation_style"] = "step-by-step"
        if "short" in lower or "concise" in lower:
            preferences["response_length"] = "short"
        if text not in preferences.get("notes", []):
            notes = list(preferences.get("notes", []))
            notes.append(text)
            preferences["notes"] = notes[-6:]
    elif kind == "goal" and text not in goals:
        goals.append(text)
    elif kind == "misconception" and text not in misconceptions:
        misconceptions.append(text)
        mastery[topic] = "needs support"
    elif kind == "mastery":
        mastery[topic] = "mastered"
    elif kind == "progress":
        mastery[topic] = "improving"
        profile.progress_summary = text

    profile.preferences_json = preferences
    profile.goals_json = goals[-10:]
    profile.mastery_json = mastery
    profile.misconceptions_json = misconceptions[-10:]
    db.commit()
    db.refresh(profile)
    return profile


def progress_snapshot(db: OrmSession, user_id: int) -> dict:
    profile = get_or_create_profile(db, user_id)
    sessions_count = db.query(func.count(Session.id)).filter(Session.user_id == user_id).scalar() or 0
    messages_count = db.query(func.count(Message.id)).filter(Message.user_id == user_id).scalar() or 0
    memories_count = (
        db.query(func.count(MemoryEntry.id))
        .filter(MemoryEntry.user_id == user_id, MemoryEntry.status == "active")
        .scalar()
        or 0
    )
    mastery = profile.mastery_json or {}
    weak_topics = [topic for topic, status in mastery.items() if status == "needs support"]
    mastered_topics = [topic for topic, status in mastery.items() if status == "mastered"]
    suggested = weak_topics[0] if weak_topics else (profile.goals_json[0] if profile.goals_json else "Review recent mistakes")
    return {
        "sessions_count": sessions_count,
        "messages_count": messages_count,
        "memories_count": memories_count,
        "weak_topics": weak_topics,
        "mastered_topics": mastered_topics,
        "recent_progress_summary": profile.progress_summary,
        "suggested_next_topic": suggested,
    }

