from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.services.memory_manager import memory_manager


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def auth_headers(email="student@example.com"):
    response = client.post(
        "/auth/register",
        json={"name": "Test Student", "email": email, "password": "secret123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_registration_login_and_me():
    response = client.post(
        "/auth/register",
        json={"name": "Ada Student", "email": "ada@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    login = client.post("/auth/login", json={"email": "ada@example.com", "password": "secret123"})
    assert login.status_code == 200
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ada@example.com"


def test_create_chat_session_and_send_message():
    headers = auth_headers("chat@example.com")
    session_response = client.post(
        "/chat/sessions",
        json={"topic": "algebra", "title": "Fractions"},
        headers=headers,
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]
    message_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        json={
            "message_text": "I always get confused by fractions and prefer step-by-step explanations.",
            "mode": "hybrid_memory",
        },
        headers=headers,
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    assert "guided hints" in payload["response_text"]
    assert payload["stored_memories"]


def test_memory_extraction_retrieval_and_deletion():
    headers = auth_headers("memory@example.com")
    facts = memory_manager.extract_facts(
        "My goal is to improve algebra because I struggle with fractions.",
        "Tutor response",
        "algebra",
    )
    assert any(fact["memory_type"] == "misconception" for fact in facts)
    created = client.post(
        "/memory",
        json={
            "memory_text": "Student struggles with fractions.",
            "memory_type": "misconception",
            "topic_tag": "algebra",
            "importance_score": 5,
            "confidence_score": 0.9,
        },
        headers=headers,
    )
    assert created.status_code == 200
    memory_id = created.json()["id"]
    retrieved = client.post(
        "/memory/retrieve",
        json={"query": "fraction algebra", "topic": "algebra", "top_k": 3},
        headers=headers,
    )
    assert retrieved.status_code == 200
    assert retrieved.json()
    deleted = client.delete(f"/memory/{memory_id}", headers=headers)
    assert deleted.status_code == 200
    after_delete = client.post(
        "/memory/retrieve",
        json={"query": "fraction algebra", "topic": "algebra", "top_k": 3},
        headers=headers,
    )
    assert all(item["id"] != memory_id for item in after_delete.json())


def test_profile_update_and_progress():
    headers = auth_headers("profile@example.com")
    profile = client.put(
        "/profile",
        json={
            "preferences_json": {
                "explanation_style": "visual",
                "response_length": "short",
                "tone": "calm",
            },
            "goals_json": ["Improve geometry"],
            "mastery_json": {"geometry": "needs support"},
            "misconceptions_json": ["Confuses radius and diameter"],
            "progress_summary": "Started geometry practice.",
        },
        headers=headers,
    )
    assert profile.status_code == 200
    progress = client.get("/profile/progress", headers=headers)
    assert progress.status_code == 200
    assert "geometry" in progress.json()["weak_topics"]


def test_evaluation_run():
    headers = auth_headers("eval@example.com")
    response = client.post(
        "/eval/run",
        json={"model_mode": "hybrid_memory", "dataset": "Demo"},
        headers=headers,
    )
    assert response.status_code == 200
    assert "memory_precision" in response.json()["metrics"]
    results = client.get("/eval/results", headers=headers)
    assert results.status_code == 200
    assert results.json()

