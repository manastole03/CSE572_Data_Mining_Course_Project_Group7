# Memory Tutor Class Demo: Step-by-Step Process

Use this with the PowerPoint for a 5-minute class presentation.

## 0. Before Class Setup

Open two terminals.

Terminal 1 - backend:

```bash
cd "/Users/manastole/Downloads/Notebook-main 2/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Terminal 2 - frontend:

```bash
cd "/Users/manastole/Downloads/Notebook-main 2/frontend"
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Demo account:

```text
demo@memorytutor.com
demo1234
```

## 1. Opening Explanation

What to say:

“My project is called Beyond the Chat Window. The main problem is that most AI tutors are stateless. They can help in one conversation, but they forget the student’s goals, weak areas, misconceptions, and preferred explanation style when the session ends. This app adds persistent memory so the tutor can personalize future sessions.”

Show slide:

- Slide 1: title
- Slide 2: problem and goal

## 2. Explain Architecture

Show slide:

- Slide 3: Multi-Agent Architecture

What to say:

“The system uses two main agents. The Tutor Agent generates scaffolded tutoring responses. The Memory Manager Agent decides what facts are useful, stores them, retrieves relevant memory, updates the student profile, summarizes memories, and deletes memories when requested.”

Point out:

- React/Vite frontend
- FastAPI backend
- SQLite for structured data
- ChromaDB for episodic vector memory
- Structured profile memory
- Simulated LoRA/profile personalization mode

## 3. Login And Dashboard Demo

In browser:

1. Go to `http://127.0.0.1:5173`
2. Click **Use demo student**
3. Land on **Dashboard**

What to say:

“This dashboard is the student’s home page. It shows recent sessions, weak areas, memory count, progress summary, and a suggested next topic. The idea is that learning history is visible, not hidden inside the model.”

Point out:

- Stored memories
- Current weak areas
- Recent sessions
- Progress summary
- Start new session button

## 4. Tutor Chat Demo

In browser:

1. Click **Tutor Chat**
2. Use topic: `algebra`
3. Keep mode: `hybrid_memory`
4. Type this prompt:

```text
I always get confused by fractions and prefer step-by-step explanations.
```

5. Click **Send**

What to say before sending:

“This is a useful learner message because it contains both a misconception and a preference. The tutor should not just give an answer. It should guide the student with hints and also remember useful information for future sessions.”

What to say after response:

“The tutor responds with guided hints instead of jumping to a final answer. Behind the scenes, the Memory Manager extracts facts like ‘student struggles with fractions’ and ‘student prefers step-by-step explanations.’”

Point out:

- Student message bubble
- Tutor response bubble
- Mode selector
- Current topic
- Memories used panel

## 5. Show Memory Center

In browser:

1. Click **Memory Center**
2. Search for:

```text
fractions
```

3. Show the stored memory
4. Filter by type: `misconception`
5. Click **Edit** on a memory
6. Change text slightly, for example:

```text
Student struggles with fractions but improves when steps are separated clearly.
```

7. Click **Save**

What to say:

“This page is important because memory is user-facing. The student can inspect what the system remembers, edit incorrect or outdated memory, manually add memory, summarize related memories, and delete memory.”

Point out:

- Memory text
- Memory type
- Topic tag
- Importance score
- Confidence score
- Source session
- Timestamp
- Edit and delete controls

## 6. Show Delete / Forgetting Control

In browser:

1. Pick a memory
2. Click **Delete**
3. Confirm delete
4. Search for the deleted memory again

What to say:

“Deleting a memory removes it from active SQL results and from vector retrieval. This is part of forgetting control. The app tracks deleted status for audit purposes, but deleted memories should not be used in future tutor responses.”

Important explanation:

“This is not a formal mathematical privacy proof. It is a practical MVP deletion and retrieval-control mechanism.”

## 7. Show Student Profile

In browser:

1. Click **Profile**
2. Show:
   - Preferred explanation style
   - Response length
   - Tone
   - Learning goals
   - Known weak areas
   - Mastered topics
   - Progress summary

What to say:

“Episodic memory stores specific facts, but the structured profile stores compact long-term personalization signals. This profile acts like a simulated parametric memory or LoRA-style personalization layer in the MVP.”

Optional action:

- Change preferred explanation style to `visual`
- Click **Save profile**

## 8. Show Progress Analytics

In browser:

1. Click **Progress**

What to say:

“The progress page turns memory into learning analytics. It summarizes the number of sessions, messages, stored memories, weak topics, mastered topics, and suggested next topic.”

Point out:

- Sessions count
- Messages count
- Stored memories
- Weak topics
- Mastered topics
- Suggested next topic

## 9. Show Evaluation Dashboard

In browser:

1. Click **Evaluation**
2. Select baseline mode:

```text
hybrid_memory
```

3. Select dataset:

```text
Demo
```

4. Click **Run evaluation**

What to say:

“The evaluation dashboard compares memory strategies. The MVP stores mock evaluation metrics, but the structure is ready for real MathDial, PersonaMem-v2, and LoCoMo evaluation later.”

Explain modes:

- `no_memory`: ignores memory
- `naive_rag`: uses prior messages or raw retrieval only
- `lora_only`: uses profile preference only
- `hybrid_memory`: uses profile plus episodic vector memory

Explain metrics:

- Memory precision: are stored facts useful?
- Memory recall: did the system remember key facts?
- Personalization score: did the response fit the learner?
- Forgetting leakage rate: did deleted memory leak back?
- Latency: response time cost
- Token usage: prompt/response efficiency
- Storage growth: how fast memory grows

## 10. Closing Explanation

Show slide:

- Slide 8: Takeaways

What to say:

“The main takeaway is that tutoring memory should be persistent, personalized, controllable, and measurable. This MVP demonstrates the full flow: authentication, chat, memory extraction, vector retrieval, profile updates, memory controls, progress analytics, and evaluation.”

## 5-Minute Timing Plan

| Time | Section |
| --- | --- |
| 0:00-0:40 | Problem and project goal |
| 0:40-1:20 | Architecture |
| 1:20-2:20 | Login, dashboard, tutor chat |
| 2:20-3:20 | Memory Center edit/delete |
| 3:20-4:10 | Profile and progress |
| 4:10-4:45 | Evaluation dashboard |
| 4:45-5:00 | Takeaways |

## Backup Plan If Live Demo Fails

If backend is not running:

```bash
cd "/Users/manastole/Downloads/Notebook-main 2/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

If frontend is not running:

```bash
cd "/Users/manastole/Downloads/Notebook-main 2/frontend"
npm run dev
```

If login fails:

- Click **Use demo student**
- Or register a new account with any valid email

If evaluation feels too abstract:

Say:

“For MVP, the evaluation numbers are mocked, but they are stored in the database and structured exactly like real benchmark results would be. This lets future work plug in MathDial, PersonaMem-v2, and LoCoMo.”

## One-Sentence Summary

“This app turns a stateless AI tutor into a persistent personalized learning system by combining a Tutor Agent, a Memory Manager Agent, episodic vector memory, structured profile memory, user memory controls, and an evaluation dashboard.”

