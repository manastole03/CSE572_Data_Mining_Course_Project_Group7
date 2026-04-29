from __future__ import annotations

from typing import Any

from app.config import settings
from app.models import Session, User
from app.models.models import Message
from app.models import StudentProfile


class TutorAgent:
    def generate_response(
        self,
        user: User,
        session: Session,
        message: str,
        retrieved_memories: list[Any],
        profile: StudentProfile,
        mode: str,
    ) -> str:
        if settings.openai_api_key:
            try:
                return self._openai_response(user, session, message, retrieved_memories, profile, mode)
            except Exception:
                pass
        return self._mock_response(user, session, message, retrieved_memories, profile, mode)

    def raw_prior_message_memories(self, messages: list[Message], query: str, limit: int = 5) -> list[dict[str, Any]]:
        query_terms = set(query.lower().split())
        scored = []
        for message in messages:
            if message.sender_type != "student":
                continue
            terms = set(message.message_text.lower().split())
            score = len(query_terms & terms) / max(len(query_terms | terms), 1)
            if score > 0:
                scored.append((message, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            {
                "id": message.id,
                "memory_text": message.message_text,
                "memory_type": "prior_message",
                "topic_tag": "session_history",
                "relevance_score": score,
            }
            for message, score in scored[:limit]
        ]

    def _mock_response(
        self,
        user: User,
        session: Session,
        message: str,
        retrieved_memories: list[Any],
        profile: StudentProfile,
        mode: str,
    ) -> str:
        preferences = profile.preferences_json or {}
        style = preferences.get("explanation_style", "step-by-step")
        tone = preferences.get("tone", "encouraging")
        response_length = preferences.get("response_length", "medium")
        lower = message.lower()
        memory_notes = self._memory_notes(retrieved_memories)
        profile_notes = ""
        if mode in {"lora_only", "hybrid_memory"}:
            profile_notes = (
                f"I'll use your preferred {style} explanation style, a {tone} tone, "
                f"and {response_length} length."
            )
        concept = self._concept_lesson(lower, session.topic)
        if mode == "no_memory":
            memory_notes = "I am answering without stored memory for this baseline."
            profile_notes = ""
        elif mode == "lora_only":
            memory_notes = "I am using profile preferences only, not episodic memory."
        elif mode == "naive_rag":
            profile_notes = "I am using prior conversation snippets only for this baseline."

        parts = [
            f"Hi {user.name}, let's work through this with guided hints rather than jumping to a final answer.",
            profile_notes,
            memory_notes,
            concept,
            "Try this check: what is the first rule, definition, or quantity you would use?",
        ]
        return "\n\n".join(part for part in parts if part)

    def _concept_lesson(self, lower: str, topic: str) -> str:
        text = f"{topic} {lower}".lower()
        if "fraction" in text:
            return (
                "For fractions, first make the denominators visible and handle signs carefully. "
                "Hint 1: rewrite each term so the numerator and denominator are clear. "
                "Hint 2: only combine terms after the denominators match."
            )
        if "algebra" in text or "equation" in text:
            return (
                "For algebra, keep both sides balanced. Hint 1: simplify each side. "
                "Hint 2: undo operations in reverse order. Hint 3: check the solution by substituting it back."
            )
        if "derivative" in text or "calculus" in text:
            return (
                "A derivative is an instant rate of change. Hint 1: identify the function and variable. "
                "Hint 2: choose the matching rule, such as power, product, chain, or quotient."
            )
        return (
            "Start by naming the concept, then solve a smaller version of the problem. "
            "I will give the next hint after your attempt."
        )

    def _memory_notes(self, memories: list[Any]) -> str:
        if not memories:
            return "No relevant stored memories were used for this turn."
        rendered = []
        for item in memories[:3]:
            if isinstance(item, tuple):
                memory, score = item
                rendered.append(f"- {memory.memory_text} (relevance {score:.2f})")
            elif isinstance(item, dict):
                rendered.append(f"- {item.get('memory_text', '')} (prior message)")
        return "Memories used:\n" + "\n".join(rendered)

    def _openai_response(
        self,
        user: User,
        session: Session,
        message: str,
        retrieved_memories: list[Any],
        profile: StudentProfile,
        mode: str,
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        memory_text = self._memory_notes(retrieved_memories)
        prompt = f"""
You are a persistent personalized tutoring agent. Use scaffolded hints and guiding questions.
Student: {user.name}
Topic: {session.topic}
Mode: {mode}
Profile: {profile.preferences_json}, goals={profile.goals_json}, weak areas={profile.misconceptions_json}
Retrieved memory: {memory_text}
Student message: {message}
"""
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content or self._mock_response(
            user, session, message, retrieved_memories, profile, mode
        )


tutor_agent = TutorAgent()

