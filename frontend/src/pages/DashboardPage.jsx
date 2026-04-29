import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { adminApi, chatApi, memoryApi, profileApi } from "../api/tutor";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [state, setState] = useState({ sessions: [], memories: [], progress: null, stats: null });

  useEffect(() => {
    Promise.all([chatApi.listSessions(), memoryApi.list(), profileApi.progress(), adminApi.stats()]).then(
      ([sessions, memories, progress, stats]) => setState({ sessions, memories, progress, stats })
    );
  }, []);

  const startSession = async () => {
    const session = await chatApi.createSession({ topic: "general tutoring", title: "New Tutoring Session" });
    navigate(`/chat/${session.id}`);
  };

  const lastSession = state.sessions[0];
  const progress = state.progress || {};

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="text-sm font-semibold text-indigo-600">Student Dashboard</p>
            <h2 className="mt-1 text-3xl font-bold text-ink">Welcome, {user?.name}</h2>
            <p className="mt-2 max-w-2xl text-slate-600">
              Your tutor remembers learning goals, weak areas, preferences, and progress across sessions.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-secondary" disabled={!lastSession} onClick={() => navigate(`/chat/${lastSession.id}`)}>
              Continue last session
            </button>
            <button className="btn-primary" onClick={startSession}>Start new session</button>
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Sessions" value={progress.sessions_count ?? "-"} />
        <StatCard label="Messages" value={progress.messages_count ?? "-"} />
        <StatCard label="Stored memories" value={state.memories.length} />
        <StatCard label="Suggested next topic" value={progress.suggested_next_topic || "Review"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <section className="card p-5">
          <h3 className="text-lg font-bold text-ink">Recent Sessions</h3>
          <div className="mt-4 space-y-3">
            {state.sessions.length === 0 ? (
              <p className="text-sm text-slate-500">No sessions yet. Start one to begin building memory.</p>
            ) : (
              state.sessions.slice(0, 5).map((session) => (
                <button
                  key={session.id}
                  className="w-full rounded-xl border border-slate-200 p-4 text-left hover:bg-slate-50"
                  onClick={() => navigate(`/chat/${session.id}`)}
                >
                  <p className="font-semibold text-ink">{session.title}</p>
                  <p className="text-sm text-slate-500">{session.topic} - {session.status}</p>
                </button>
              ))
            )}
          </div>
        </section>
        <section className="card p-5">
          <h3 className="text-lg font-bold text-ink">Current Weak Areas</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {(progress.weak_topics || []).length === 0 ? (
              <p className="text-sm text-slate-500">Weak areas will appear as the tutor learns from your work.</p>
            ) : (
              progress.weak_topics.map((topic) => (
                <span key={topic} className="rounded-full bg-rose-50 px-3 py-1 text-sm font-semibold text-rose-700">
                  {topic}
                </span>
              ))
            )}
          </div>
          <h3 className="mt-6 text-lg font-bold text-ink">Progress Summary</h3>
          <p className="mt-2 text-sm text-slate-600">{progress.recent_progress_summary || "No summary yet."}</p>
        </section>
      </div>
    </div>
  );
}

