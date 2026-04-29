# Persistent Memory Tutor Backend

FastAPI backend for **Beyond the Chat Window: Multi-Agent Memory for Persistent, Personalized Learning**.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional `.env` or shell variables:

```bash
JWT_SECRET_KEY=change-me
OPENAI_API_KEY=optional
OPENAI_MODEL=gpt-4o-mini
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Run

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

## Demo Login

Use the frontend **Demo Login** button or call:

```bash
curl -X POST http://127.0.0.1:8001/auth/demo
```

Demo credentials:

```text
demo@memorytutor.com
demo1234
```
