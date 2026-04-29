# Beyond the Chat Window: Multi-Agent Memory for Persistent, Personalized Learning

This workspace contains a complete full-stack MVP for a persistent, personalized AI tutoring assistant. The app solves the common stateless tutor problem by storing useful learner information across sessions: goals, misconceptions, weak areas, mastered topics, preferences, and progress.

The requested standalone implementation lives in:

```text
backend/
frontend/
```

The older Notebook/MindPaper files are still present in the repository, but the new Memory Tutor app runs from those two folders.

## Architecture

Frontend:

- React with Vite
- React Router protected routes
- Axios API client
- Tailwind CSS academic/AI SaaS UI
- Pages for dashboard, tutor chat, memory center, profile, progress, and evaluation

Backend:

- FastAPI
- SQLite local database
- SQLAlchemy ORM
- Pydantic schemas
- JWT auth
- bcrypt password hashing
- ChromaDB vector memory
- Deterministic local embedding abstraction
- Modular services for tutor, memory manager, vector store, profile, and evaluation

Agent layer:

- `TutorAgent` generates scaffolded tutoring responses.
- `MemoryManager` extracts learner facts, scores importance, stores/retrieves/updates/summarizes/deletes memory, and updates student profiles.
- Mock responses run by default without paid API keys.
- Optional `OPENAI_API_KEY` support can be enabled through environment variables.

## Folder Structure

```text
backend/
  app/
    main.py
    database.py
    config.py
    models/
    schemas/
    routes/
    services/
      tutor_agent.py
      memory_manager.py
      vector_store.py
      profile_service.py
      evaluation_service.py
    utils/
    tests/
  requirements.txt
  README.md

frontend/
  src/
    api/
    components/
    context/
    pages/
    routes/
    styles/
    App.jsx
    main.jsx
  package.json
  README.md
```

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment variables:

```bash
export JWT_SECRET_KEY=change-me
export OPENAI_API_KEY=optional
export OPENAI_MODEL=gpt-4o-mini
export CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Run the API:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

API health check:

```text
http://127.0.0.1:8001/
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Optional frontend environment variable:

```bash
VITE_API_URL=http://127.0.0.1:8001
```

## Demo Login

Use the **Use demo student** button on `/login`, or use:

```text
Email: demo@memorytutor.com
Password: demo1234
```

The demo flow creates:

- Demo student
- Sample tutoring session
- Step-by-step preference memory
- Fractions misconception memory
- Algebra improvement goal
- Derivatives progress memory

## Main Features

- Student registration and login
- JWT protected routes and APIs
- Password hashes stored with bcrypt
- Student dashboard with recent sessions, weak areas, memory count, and progress summary
- Tutor chat with session creation, history, baseline mode selection, current topic, and memories-used panel
- Tutor modes: `no_memory`, `naive_rag`, `lora_only`, `hybrid_memory`
- Automatic memory extraction from tutor interactions
- Episodic memory retrieval through ChromaDB
- Structured student profile memory
- Simulated LoRA/profile personalization
- User-facing memory search, filter, add, edit, delete, and summarize controls
- Profile editing for preferred style, response length, tone, goals, weak areas, mastered topics, and progress
- Progress analytics cards and topic bars
- Evaluation dashboard for precision, recall, personalization, forgetting leakage, latency, token usage, and storage growth
- Stored evaluation logs

## API Overview

Auth:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
POST /auth/demo
```

Chat:

```text
POST  /chat/sessions
GET   /chat/sessions
GET   /chat/sessions/{session_id}
POST  /chat/sessions/{session_id}/messages
PATCH /chat/sessions/{session_id}/end
```

Memory:

```text
GET    /memory
GET    /memory/{memory_id}
POST   /memory
PUT    /memory/{memory_id}
DELETE /memory/{memory_id}
POST   /memory/retrieve
POST   /memory/summarize
```

Profile:

```text
GET /profile
PUT /profile
PUT /profile/preferences
GET /profile/progress
```

Evaluation:

```text
POST /eval/run
GET  /eval/results
GET  /eval/results/{run_id}
```

Admin:

```text
GET  /admin/system-stats
POST /admin/seed-demo
```

## Tests

Backend:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Frontend:

```bash
cd frontend
npm run build
```

## Data Storage

Local runtime data is stored under:

```text
backend/data/
```

SQLite database:

```text
backend/data/memory_tutor.db
```

ChromaDB vector store:

```text
backend/data/chroma/
```

## Future Work

- Replace mock evaluation metrics with full MathDial, PersonaMem-v2, and LoCoMo dataset runners.
- Add true LoRA/PEFT training jobs and adapter selection.
- Add teacher/admin role permissions.
- Add richer charts for mastery over time.
- Add formal privacy and deletion verification beyond the local audit.
