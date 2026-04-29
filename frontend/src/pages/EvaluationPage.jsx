import { useEffect, useState } from "react";

import { evalApi } from "../api/tutor";
import StatCard from "../components/StatCard.jsx";
import { useToast } from "../context/ToastContext.jsx";

const modes = ["no_memory", "naive_rag", "lora_only", "hybrid_memory"];
const datasets = ["Demo", "MathDial", "PersonaMem-v2", "LoCoMo"];

export default function EvaluationPage() {
  const { showToast } = useToast();
  const [modelMode, setModelMode] = useState("hybrid_memory");
  const [dataset, setDataset] = useState("Demo");
  const [runs, setRuns] = useState([]);
  const [latest, setLatest] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => setRuns(await evalApi.results());

  useEffect(() => {
    load();
  }, []);

  const run = async () => {
    setLoading(true);
    try {
      const result = await evalApi.run({ model_mode: modelMode, dataset });
      setLatest(result);
      await load();
      showToast("Evaluation run stored.");
    } finally {
      setLoading(false);
    }
  };

  const metrics = latest?.metrics || runs[0]?.metrics || {};

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h2 className="text-2xl font-bold text-ink">Evaluation Dashboard</h2>
            <p className="mt-2 text-sm text-slate-500">Compare memory modes across tutoring-style datasets. MVP metrics are mocked but stored with real run records.</p>
          </div>
          <div className="grid gap-2 md:grid-cols-[180px_180px_auto]">
            <select className="input" value={modelMode} onChange={(e) => setModelMode(e.target.value)}>
              {modes.map((mode) => <option key={mode}>{mode}</option>)}
            </select>
            <select className="input" value={dataset} onChange={(e) => setDataset(e.target.value)}>
              {datasets.map((item) => <option key={item}>{item}</option>)}
            </select>
            <button className="btn-primary" onClick={run} disabled={loading}>{loading ? "Running..." : "Run evaluation"}</button>
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Memory precision" value={metrics.memory_precision ?? "-"} />
        <StatCard label="Memory recall" value={metrics.memory_recall ?? "-"} />
        <StatCard label="Personalization" value={metrics.personalization_score ?? "-"} />
        <StatCard label="Leakage rate" value={metrics.forgetting_leakage_rate ?? "-"} />
        <StatCard label="Latency ms" value={metrics.latency_ms ?? "-"} />
        <StatCard label="Token usage" value={metrics.token_usage ?? "-"} />
        <StatCard label="Storage growth" value={metrics.storage_growth ?? "-"} />
      </div>

      <section className="card p-5">
        <h3 className="font-bold text-ink">Stored Evaluation Runs</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2">Run</th>
                <th>Mode</th>
                <th>Dataset</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>Personalization</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.run_id} className="border-b border-slate-100">
                  <td className="py-2 font-medium">{run.run_id}</td>
                  <td>{run.model_mode}</td>
                  <td>{run.dataset}</td>
                  <td>{run.metrics.memory_precision}</td>
                  <td>{run.metrics.memory_recall}</td>
                  <td>{run.metrics.personalization_score}</td>
                  <td>{new Date(run.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

