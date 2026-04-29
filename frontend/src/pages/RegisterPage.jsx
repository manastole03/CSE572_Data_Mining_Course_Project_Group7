import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { errorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import { AuthShell } from "./LoginPage.jsx";

export default function RegisterPage() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (error) {
      showToast(errorMessage(error), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Create your tutor memory" subtitle="Your account keeps sessions, profile, and memories private.">
      <form className="space-y-4" onSubmit={submit}>
        <div>
          <label className="label">Name</label>
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </div>
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
          {loading ? "Creating..." : "Register"}
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-slate-500">
        Already registered? <Link className="font-semibold text-indigo-600" to="/login">Login</Link>
      </p>
    </AuthShell>
  );
}

