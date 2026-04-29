import { useEffect, useState } from "react";

import { errorMessage } from "../api/client";
import { memoryApi } from "../api/tutor";
import ConfirmModal from "../components/ConfirmModal.jsx";
import { useToast } from "../context/ToastContext.jsx";

const memoryTypes = ["", "misconception", "preference", "goal", "mastery", "progress", "summary", "other"];

export default function MemoryPage() {
  const { showToast } = useToast();
  const [memories, setMemories] = useState([]);
  const [filters, setFilters] = useState({ search: "", memory_type: "", topic: "" });
  const [draft, setDraft] = useState({
    memory_text: "",
    memory_type: "other",
    topic_tag: "general",
    importance_score: 3,
    confidence_score: 0.7
  });
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = async () => {
    const params = {
      search: filters.search || undefined,
      memory_type: filters.memory_type || undefined,
      topic: filters.topic || undefined
    };
    setMemories(await memoryApi.list(params));
  };

  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    if (!draft.memory_text.trim()) return;
    try {
      await memoryApi.create(draft);
      setDraft({ memory_text: "", memory_type: "other", topic_tag: "general", importance_score: 3, confidence_score: 0.7 });
      await load();
      showToast("Memory added.");
    } catch (error) {
      showToast(errorMessage(error), "error");
    }
  };

  const saveEdit = async () => {
    try {
      await memoryApi.update(editing.id, editing);
      setEditing(null);
      await load();
      showToast("Memory updated.");
    } catch (error) {
      showToast(errorMessage(error), "error");
    }
  };

  const confirmDelete = async () => {
    await memoryApi.delete(deleteTarget.id);
    setDeleteTarget(null);
    await load();
    showToast("Memory deleted from active SQL results and vector retrieval.");
  };

  const summarize = async () => {
    const summaries = await memoryApi.summarize();
    await load();
    showToast(`${summaries.length} summary memories created.`);
  };

  return (
    <div className="space-y-6">
      <section className="card p-5">
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
          <div>
            <h2 className="text-2xl font-bold text-ink">Memory Center</h2>
            <p className="text-sm text-slate-500">Inspect, search, edit, delete, and manually seed tutor memory.</p>
          </div>
          <button className="btn-secondary" onClick={summarize}>Summarize related memories</button>
        </div>
      </section>

      <section className="card p-5">
        <h3 className="font-bold text-ink">Add manual memory</h3>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1.5fr_160px_160px_120px_120px_auto]">
          <input className="input" placeholder="Memory text" value={draft.memory_text} onChange={(e) => setDraft({ ...draft, memory_text: e.target.value })} />
          <select className="input" value={draft.memory_type} onChange={(e) => setDraft({ ...draft, memory_type: e.target.value })}>
            {memoryTypes.filter(Boolean).map((type) => <option key={type}>{type}</option>)}
          </select>
          <input className="input" value={draft.topic_tag} onChange={(e) => setDraft({ ...draft, topic_tag: e.target.value })} />
          <input className="input" type="number" min="1" max="5" value={draft.importance_score} onChange={(e) => setDraft({ ...draft, importance_score: Number(e.target.value) })} />
          <input className="input" type="number" min="0" max="1" step="0.1" value={draft.confidence_score} onChange={(e) => setDraft({ ...draft, confidence_score: Number(e.target.value) })} />
          <button className="btn-primary" onClick={create}>Add</button>
        </div>
      </section>

      <section className="card p-5">
        <div className="grid gap-3 md:grid-cols-[1fr_180px_180px_auto]">
          <input className="input" placeholder="Search memories" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
          <select className="input" value={filters.memory_type} onChange={(e) => setFilters({ ...filters, memory_type: e.target.value })}>
            {memoryTypes.map((type) => <option key={type} value={type}>{type || "all types"}</option>)}
          </select>
          <input className="input" placeholder="Topic filter" value={filters.topic} onChange={(e) => setFilters({ ...filters, topic: e.target.value })} />
          <button className="btn-secondary" onClick={load}>Search</button>
        </div>
      </section>

      <section className="space-y-3">
        {memories.length === 0 ? (
          <div className="card p-10 text-center text-slate-500">No active memories yet.</div>
        ) : (
          memories.map((memory) => (
            <div key={memory.id} className="card p-5">
              {editing?.id === memory.id ? (
                <div className="space-y-3">
                  <textarea className="input min-h-24" value={editing.memory_text} onChange={(e) => setEditing({ ...editing, memory_text: e.target.value })} />
                  <div className="grid gap-3 md:grid-cols-4">
                    <select className="input" value={editing.memory_type} onChange={(e) => setEditing({ ...editing, memory_type: e.target.value })}>
                      {memoryTypes.filter(Boolean).map((type) => <option key={type}>{type}</option>)}
                    </select>
                    <input className="input" value={editing.topic_tag} onChange={(e) => setEditing({ ...editing, topic_tag: e.target.value })} />
                    <input className="input" type="number" min="1" max="5" value={editing.importance_score} onChange={(e) => setEditing({ ...editing, importance_score: Number(e.target.value) })} />
                    <input className="input" type="number" min="0" max="1" step="0.1" value={editing.confidence_score} onChange={(e) => setEditing({ ...editing, confidence_score: Number(e.target.value) })} />
                  </div>
                  <div className="flex gap-2">
                    <button className="btn-primary" onClick={saveEdit}>Save</button>
                    <button className="btn-secondary" onClick={() => setEditing(null)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex flex-col justify-between gap-3 md:flex-row">
                    <div>
                      <p className="font-semibold text-ink">{memory.memory_text}</p>
                      <p className="mt-2 text-sm text-slate-500">
                        {memory.memory_type} - {memory.topic_tag} - source session {memory.session_id || "manual"}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn-secondary" onClick={() => setEditing(memory)}>Edit</button>
                      <button className="btn-secondary text-rose-700" onClick={() => setDeleteTarget(memory)}>Delete</button>
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 md:grid-cols-3">
                    <Score label="Importance" value={memory.importance_score} max={5} />
                    <Score label="Confidence" value={memory.confidence_score} max={1} />
                    <p className="text-sm text-slate-500">Updated {new Date(memory.updated_at).toLocaleString()}</p>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </section>

      {deleteTarget && (
        <ConfirmModal
          title="Delete memory?"
          body="This removes the memory from active SQL results and vector retrieval. It remains marked deleted for audit."
          onCancel={() => setDeleteTarget(null)}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}

function Score({ label, value, max }) {
  const pct = Math.min(100, (Number(value) / max) * 100);
  return (
    <div>
      <p className="text-xs font-semibold uppercase text-slate-500">{label}: {value}</p>
      <div className="mt-1 h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-indigo-500" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

