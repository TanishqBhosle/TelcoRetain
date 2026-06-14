import { FormEvent, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { Cable } from "lucide-react";
import { api, unwrap } from "../lib/api";
import { useAuthStore } from "../state/auth";

type User = {
  id: string;
  email: string;
  full_name: string;
  role?: { name: string };
};

export function SignUpPage() {
  const { accessToken, setSession } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  if (accessToken) return <Navigate to="/" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await unwrap<User>(api.post("/auth/register", { email, password, full_name: fullName }));
      setSuccess("Account created! Please check your email to verify your account.");
    } catch {
      setError("Registration failed. The email may already be in use.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="brand auth-brand">
          <Cable size={26} />
          <span>Telco Retain</span>
        </div>
        <h2 style={{ margin: "0 0 18px", fontSize: 18 }}>Create Account</h2>
        <form onSubmit={submit} className="form">
          <label>
            Full Name
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} type="text" autoComplete="name" required />
          </label>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
          </label>
          <label>
            Password
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" autoComplete="new-password" minLength={8} required />
          </label>
          {error && <p className="error-text">{error}</p>}
          {success && <p style={{ color: "#146b45", fontSize: 13, margin: 0 }}>{success}</p>}
          <button className="primary-button" disabled={loading}>{loading ? "Creating account..." : "Sign up"}</button>
        </form>
        <p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }}>
          Already have an account? <Link to="/signin" style={{ color: "#1d8a8a", fontWeight: 700 }}>Sign in</Link>
        </p>
      </section>
    </main>
  );
}
