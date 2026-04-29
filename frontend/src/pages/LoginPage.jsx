import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { errorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import { useToast } from "../context/ToastContext.jsx";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "demo@memorytutor.com", password: "demo1234" });
  const [loading, setLoading] = useState(false);
  const { login, demoLogin } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      await login(form);
      navigate("/dashboard");
    } catch (error) {
      showToast(errorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  const useDemo = async () => {
    setLoading(true);
    try {
      await demoLogin();
      navigate("/dashboard");
    } catch (error) {
      showToast(errorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Welcome back" subtitle="Login to your persistent AI tutoring workspace.">
      <form className="space-y-4" onSubmit={submit}>
        <div>
          <label className="label">Email</label>
          <input className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className="label">Password</label>
          <input
            className="input"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Signing in..." : "Login"}
        </button>
        <button type="button" className="btn-secondary w-full" onClick={useDemo} disabled={loading}>
          Use demo student
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-slate-500">
        New here? <Link className="font-semibold text-indigo-600" to="/register">Create an account</Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-soft p-5">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">Beyond the Chat Window</p>
          <h1 className="mt-2 text-3xl font-bold text-ink">{title}</h1>
          <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
        </div>
        <div className="card p-6">{children}</div>
      </div>
    </div>
  );
}
