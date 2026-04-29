import { useEffect, useState } from "react";

import { profileApi } from "../api/tutor";
import StatCard from "../components/StatCard.jsx";

export default function ProgressPage() {
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    profileApi.progress().then(setProgress);
  }, []);

  if (!progress) return <div className="card p-8 text-slate-500">Loading progress...</div>;

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h2 className="text-2xl font-bold text-ink">Progress Analytics</h2>
        <p className="mt-2 text-sm text-slate-500">Simple learning analytics from sessions, messages, profile, and memory.</p>
      </section>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Sessions" value={progress.sessions_count} />
        <StatCard label="Messages" value={progress.messages_count} />
        <StatCard label="Stored memories" value={progress.memories_count} />
        <StatCard label="Suggested next topic" value={progress.suggested_next_topic} />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <TopicPanel title="Weak Topics" topics={progress.weak_topics} color="bg-rose-500" />
        <TopicPanel title="Mastered Topics" topics={progress.mastered_topics} color="bg-emerald-500" />
      </div>
      <section className="card p-6">
        <h3 className="font-bold text-ink">Recent Progress Summary</h3>
        <p className="mt-2 text-slate-600">{progress.recent_progress_summary}</p>
      </section>
    </div>
  );
}

function TopicPanel({ title, topics, color }) {
  return (
    <section className="card p-6">
      <h3 className="font-bold text-ink">{title}</h3>
      <div className="mt-4 space-y-3">
        {topics.length === 0 ? (
          <p className="text-sm text-slate-500">No topics yet.</p>
        ) : (
          topics.map((topic, index) => (
            <div key={topic}>
              <div className="flex justify-between text-sm">
                <span>{topic}</span>
                <span>{Math.max(30, 90 - index * 15)}%</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-slate-100">
                <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.max(30, 90 - index * 15)}%` }} />
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

