import { useEffect, useState } from "react";

import { profileApi } from "../api/tutor";
import { useAuth } from "../context/AuthContext.jsx";
import { useToast } from "../context/ToastContext.jsx";

export default function ProfilePage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    profileApi.get().then(setProfile);
  }, []);

  if (!profile) return <div className="card p-8 text-slate-500">Loading profile...</div>;

  const preferences = profile.preferences_json || {};
  const save = async () => {
    const updated = await profileApi.update(profile);
    setProfile(updated);
    showToast("Profile updated.");
  };

  const setPreference = (key, value) => {
    setProfile({ ...profile, preferences_json: { ...preferences, [key]: value } });
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <section className="card p-6">
        <h2 className="text-2xl font-bold text-ink">Student Profile</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <ReadOnly label="Name" value={user?.name} />
          <ReadOnly label="Email" value={user?.email} />
          <SelectField label="Preferred explanation style" value={preferences.explanation_style || "step-by-step"} onChange={(v) => setPreference("explanation_style", v)} options={["step-by-step", "visual", "socratic", "example-first"]} />
          <SelectField label="Preferred response length" value={preferences.response_length || "medium"} onChange={(v) => setPreference("response_length", v)} options={["short", "medium", "detailed"]} />
          <SelectField label="Preferred tone" value={preferences.tone || "encouraging"} onChange={(v) => setPreference("tone", v)} options={["encouraging", "calm", "direct", "playful"]} />
        </div>

        <JsonList title="Learning goals" items={profile.goals_json} onChange={(items) => setProfile({ ...profile, goals_json: items })} />
        <JsonList title="Known weak areas" items={profile.misconceptions_json} onChange={(items) => setProfile({ ...profile, misconceptions_json: items })} />

        <div className="mt-6">
          <label className="label">Progress summary</label>
          <textarea className="input min-h-28" value={profile.progress_summary || ""} onChange={(e) => setProfile({ ...profile, progress_summary: e.target.value })} />
        </div>
        <button className="btn-primary mt-6" onClick={save}>Save profile</button>
      </section>

      <aside className="card p-6">
        <h3 className="font-bold text-ink">Mastered Topics</h3>
        <div className="mt-3 space-y-2">
          {Object.entries(profile.mastery_json || {}).map(([topic, status]) => (
            <div key={topic} className="flex justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm">
              <span>{topic}</span>
              <span className="font-semibold text-indigo-700">{status}</span>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}

function ReadOnly({ label, value }) {
  return (
    <div>
      <label className="label">{label}</label>
      <div className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">{value}</div>
    </div>
  );
}

function SelectField({ label, value, onChange, options }) {
  return (
    <div>
      <label className="label">{label}</label>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((option) => <option key={option}>{option}</option>)}
      </select>
    </div>
  );
}

function JsonList({ title, items = [], onChange }) {
  const [draft, setDraft] = useState("");
  return (
    <div className="mt-6">
      <label className="label">{title}</label>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm">
            <span>{item}</span>
            <button className="text-rose-600" onClick={() => onChange(items.filter((x) => x !== item))}>remove</button>
          </div>
        ))}
      </div>
      <div className="mt-2 flex gap-2">
        <input className="input" value={draft} onChange={(e) => setDraft(e.target.value)} placeholder={`Add ${title.toLowerCase()}`} />
        <button className="btn-secondary" onClick={() => {
          if (!draft.trim()) return;
          onChange([...items, draft.trim()]);
          setDraft("");
        }}>Add</button>
      </div>
    </div>
  );
}

