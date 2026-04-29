from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import re
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session as OrmSession

from app.models import MemoryEntry
from app.schemas.memory import MemoryCreate, MemoryUpdate
from app.services.profile_service import update_profile_from_fact
from app.services.vector_store import vector_store


def _token_count(text: str) -> int:
    return len(re.findall(r"\w+", text.lower()))


def _overlap(a: str, b: str) -> float:
    left = set(re.findall(r"\w+", a.lower()))
    right = set(re.findall(r"\w+", b.lower()))
    if not left or not right:
        return 0.0
    return len(left & right) / max(len(left | right), 1)


class MemoryManager:
    def extract_facts(self, message_text: str, tutor_response: str, session_topic: str) -> list[dict[str, Any]]:
        lower = message_text.lower()
        facts: list[dict[str, Any]] = []
        rules = [
            (
                ["confused", "struggle", "always get", "hard for me", "mistake", "stuck"],
                "misconception",
                4.0,
                "Student has a learning difficulty: ",
            ),
            (
                ["prefer", "like", "visual", "step-by-step", "step by step", "short answer", "explain slowly"],
                "preference",
                4.0,
                "Student expressed a tutoring preference: ",
            ),
            (
                ["my goal", "goal is", "want to improve", "need to improve", "exam", "quiz"],
                "goal",
                4.0,
                "Student has a learning goal: ",
            ),
            (
                ["understand now", "got it", "makes sense", "i understand", "mastered"],
                "progress",
                3.5,
                "Student showed progress: ",
            ),
        ]
        for triggers, memory_type, importance, prefix in rules:
            if any(trigger in lower for trigger in triggers):
                facts.append(
                    {
                        "memory_text": f"{prefix}{message_text[:280]}",
                        "memory_type": memory_type,
                        "topic_tag": session_topic or "general",
                        "importance_score": importance,
                        "confidence_score": 0.7,
                    }
                )
        return facts[:5]

    def importance_score(self, fact: dict[str, Any]) -> float:
        score = float(fact.get("importance_score") or 3.0)
        if fact.get("memory_type") in {"misconception", "goal"}:
            score += 0.5
        return max(1.0, min(5.0, score))

    def store_memory(
        self,
        db: OrmSession,
        user_id: int,
        session_id: int | None,
        fact: dict[str, Any],
        source_message_id: int | None = None,
    ) -> MemoryEntry:
        fact["importance_score"] = self.importance_score(fact)
        duplicate = self._find_duplicate(db, user_id, fact)
        if duplicate:
            duplicate.memory_text = self._merge_text(duplicate.memory_text, fact["memory_text"])
            duplicate.importance_score = max(duplicate.importance_score, fact["importance_score"])
            duplicate.confidence_score = max(duplicate.confidence_score, fact.get("confidence_score", 0.7))
            duplicate.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(duplicate)
            self._index_memory(duplicate)
            update_profile_from_fact(db, user_id, self._memory_to_fact(duplicate))
            return duplicate

        memory = MemoryEntry(
            user_id=user_id,
            session_id=session_id,
            memory_text=fact["memory_text"],
            memory_type=fact.get("memory_type", "other"),
            topic_tag=fact.get("topic_tag", "general"),
            source_message_id=source_message_id,
            importance_score=fact["importance_score"],
            confidence_score=fact.get("confidence_score", 0.7),
            status="active",
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        memory.vector_id = self._index_memory(memory)
        db.commit()
        db.refresh(memory)
        update_profile_from_fact(db, user_id, self._memory_to_fact(memory))
        return memory

    def retrieve_memories(
        self,
        db: OrmSession,
        user_id: int,
        query: str,
        topic: str | None = None,
        top_k: int = 5,
    ) -> list[tuple[MemoryEntry, float]]:
        vector_matches = vector_store.query(user_id=user_id, query_text=query, top_k=top_k, topic=topic)
        results: list[tuple[MemoryEntry, float]] = []
        seen: set[int] = set()
        for match in vector_matches:
            memory = db.get(MemoryEntry, match["memory_id"])
            if memory and memory.user_id == user_id and memory.status == "active":
                results.append((memory, float(match.get("score", 0.0))))
                seen.add(memory.id)
        if len(results) < top_k:
            candidates = (
                db.query(MemoryEntry)
                .filter(MemoryEntry.user_id == user_id, MemoryEntry.status == "active")
                .all()
            )
            scored = [
                (memory, _overlap(query, memory.memory_text) + memory.importance_score / 20)
                for memory in candidates
                if memory.id not in seen and (not topic or memory.topic_tag == topic)
            ]
            scored.sort(key=lambda item: item[1], reverse=True)
            results.extend(scored[: top_k - len(results)])
        return results[:top_k]

    def update_memory(self, db: OrmSession, memory: MemoryEntry, payload: MemoryUpdate) -> MemoryEntry:
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            if value is not None:
                setattr(memory, key, value)
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        memory.vector_id = self._index_memory(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def summarize_memories(self, db: OrmSession, user_id: int) -> list[MemoryEntry]:
        active = (
            db.query(MemoryEntry)
            .filter(MemoryEntry.user_id == user_id, MemoryEntry.status == "active")
            .order_by(MemoryEntry.created_at.desc())
            .all()
        )
        groups: dict[tuple[str, str], list[MemoryEntry]] = defaultdict(list)
        for memory in active:
            groups[(memory.topic_tag, memory.memory_type)].append(memory)

        summaries = []
        for (topic, memory_type), items in groups.items():
            if len(items) < 3 or memory_type == "summary":
                continue
            text = "Summary memory for {topic}: {facts}".format(
                topic=topic,
                facts="; ".join(item.memory_text for item in items[:5])[:700],
            )
            summary = self.store_memory(
                db,
                user_id=user_id,
                session_id=items[0].session_id,
                fact={
                    "memory_text": text,
                    "memory_type": "summary",
                    "topic_tag": topic,
                    "importance_score": max(item.importance_score for item in items[:5]),
                    "confidence_score": 0.75,
                },
            )
            summaries.append(summary)
        return summaries

    def delete_memory(self, db: OrmSession, memory: MemoryEntry) -> MemoryEntry:
        memory.status = "deleted"
        memory.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        vector_store.delete_memory(memory.id)
        return memory

    def update_student_profile(self, db: OrmSession, user_id: int, extracted_facts: list[dict[str, Any]]):
        profile = None
        for fact in extracted_facts:
            profile = update_profile_from_fact(db, user_id, fact)
        return profile

    def _index_memory(self, memory: MemoryEntry) -> str:
        return vector_store.upsert_memory(
            memory.id,
            memory.memory_text,
            {
                "user_id": str(memory.user_id),
                "memory_id": str(memory.id),
                "memory_type": memory.memory_type,
                "topic_tag": memory.topic_tag,
                "status": memory.status,
                "created_at": memory.created_at.isoformat(),
            },
        )

    def _find_duplicate(self, db: OrmSession, user_id: int, fact: dict[str, Any]) -> MemoryEntry | None:
        candidates = (
            db.query(MemoryEntry)
            .filter(
                MemoryEntry.user_id == user_id,
                MemoryEntry.status == "active",
                MemoryEntry.memory_type == fact.get("memory_type", "other"),
                or_(
                    MemoryEntry.topic_tag == fact.get("topic_tag", "general"),
                    MemoryEntry.topic_tag == "general",
                ),
            )
            .all()
        )
        best = None
        best_score = 0.0
        for memory in candidates:
            score = _overlap(memory.memory_text, fact["memory_text"])
            if score > best_score:
                best = memory
                best_score = score
        return best if best and best_score >= 0.42 else None

    def _merge_text(self, existing: str, incoming: str) -> str:
        if incoming.lower() in existing.lower():
            return existing
        if existing.lower() in incoming.lower():
            return incoming
        return f"{existing}; Updated evidence: {incoming}"[:1000]

    def _memory_to_fact(self, memory: MemoryEntry) -> dict[str, Any]:
        return {
            "memory_text": memory.memory_text,
            "memory_type": memory.memory_type,
            "topic_tag": memory.topic_tag,
            "importance_score": memory.importance_score,
            "confidence_score": memory.confidence_score,
        }


memory_manager = MemoryManager()

