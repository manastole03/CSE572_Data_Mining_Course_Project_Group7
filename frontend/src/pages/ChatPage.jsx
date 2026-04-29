import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { chatApi } from "../api/tutor";
import { useToast } from "../context/ToastContext.jsx";

const modes = ["hybrid_memory", "no_memory", "naive_rag", "lora_only"];

export default function ChatPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [sessions, setSessions] = useState([]);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [topic, setTopic] = useState("algebra");
  const [title, setTitle] = useState("Tutoring Session");
  const [mode, setMode] = useState("hybrid_memory");
  const [input, setInput] = useState("");
  const [retrieved, setRetrieved] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    chatApi.listSessions().then(setSessions);
  }, []);

  useEffect(() => {
    if (sessionId) {
      chatApi.getSession(sessionId).then((data) => {
        setSession(data);
        setMessages(data.messages || []);
        setTopic(data.topic);
        setTitle(data.title);
      });
    }
  }, [sessionId]);

  const activeSessionId = useMemo(() => session?.id || Number(sessionId), [session, sessionId]);

  const createSession = async () => {
    const next = await chatApi.createSession({ topic, title });
    setSession(next);
    setMessages([]);
    navigate(`/chat/${next.id}`);
  };

  const send = async () => {
    if (!input.trim()) return;
    let targetId = activeSessionId;
    if (!targetId) {
      const next = await chatApi.createSession({ topic, title });
      setSession(next);
      targetId = next.id;
      navigate(`/chat/${next.id}`);
    }
    setLoading(true);
    try {
      const response = await chatApi.sendMessage(targetId, { message_text: input, mode });
      setInput("");
      setMessages((items) => [...items, response.user_message, response.tutor_message]);
      setRetrieved(response.retrieved_memories || []);
      showToast(`Tutor responded. ${response.metadata?.facts_extracted || 0} learner facts extracted.`);
    } catch (error) {
      showToast("Could not send tutor message.", "error");
    } finally {
      setLoading(false);
    }
  };

  const endSession = async () => {
    if (!activeSessionId) return;
    const ended = await chatApi.endSession(activeSessionId);
    setSession(ended);
    showToast("Session ended.");
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <section className="card flex min-h-[720px] flex-col overflow-hidden">
        <div className="border-b border-slate-200 p-5">
          <div className="grid gap-3 md:grid-cols-4">
            <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Session title" />
            <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Current topic" />
            <select className="input" value={mode} onChange={(e) => setMode(e.target.value)}>
              {modes.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <button className="btn-secondary" onClick={createSession}>New Session</button>
          </div>
        </div>
        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center text-slate-500">
              <div>
                <p className="text-lg font-semibold text-ink">Start a tutoring conversation</p>
                <p className="mt-2">Try: I always get confused by fractions and prefer step-by-step explanations.</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender_type === "student" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    message.sender_type === "student" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.message_text}</p>
                </div>
              </div>
            ))
          )}
        </div>
        <div className="border-t border-slate-200 p-5">
          <div className="flex gap-2">
            <input
              className="input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") send();
              }}
              placeholder="Ask for help, mention a goal, or share a misconception..."
            />
            <button className="btn-primary" onClick={send} disabled={loading}>{loading ? "Sending..." : "Send"}</button>
            <button className="btn-secondary" onClick={endSession} disabled={!activeSessionId}>End</button>
          </div>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="card p-5">
          <h3 className="font-bold text-ink">Show memories used</h3>
          <p className="mt-1 text-sm text-slate-500">Top memories retrieved for the latest tutor response.</p>
          <div className="mt-4 space-y-3">
            {retrieved.length === 0 ? (
              <p className="text-sm text-slate-500">No episodic memories retrieved yet.</p>
            ) : (
              retrieved.map((memory) => (
                <div key={memory.id} className="rounded-xl border border-slate-200 p-3">
                  <p className="text-sm font-semibold text-ink">{memory.memory_text}</p>
                  <p className="mt-1 text-xs text-slate-500">{memory.memory_type} - relevance {memory.relevance_score?.toFixed?.(2)}</p>
                </div>
              ))
            )}
          </div>
        </section>
        <section className="card p-5">
          <h3 className="font-bold text-ink">Recent sessions</h3>
          <div className="mt-3 space-y-2">
            {sessions.slice(0, 6).map((item) => (
              <button key={item.id} className="block w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-slate-50" onClick={() => navigate(`/chat/${item.id}`)}>
                {item.title}
              </button>
            ))}
          </div>
        </section>
      </aside>
    </div>
  );
}

