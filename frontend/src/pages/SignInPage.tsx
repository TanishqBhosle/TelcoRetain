import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Cable } from "lucide-react";
import { api, unwrap } from "../lib/api";
import { useAuthStore } from "../state/auth";

type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

type User = {
  id: string;
  email: string;
  full_name: string;
  role?: { name: string };
};

export function SignInPage() {
  const navigate = useNavigate();
  const { accessToken, setSession, setUser } = useAuthStore();
  const [email, setEmail] = useState("admin@telecom-retention.com");
  const [password, setPassword] = useState("Admin@1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (accessToken) return <Navigate to="/" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const tokens = await unwrap<TokenResponse>(api.post("/auth/login", { email, password }));
      setSession(tokens.access_token, tokens.refresh_token);
      const user = await unwrap<User>(api.get("/auth/me"));
      setUser(user);
      navigate("/");
    } catch (err) {
      setError("Sign in failed. Check credentials and backend availability.");
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
        <form onSubmit={submit} className="form">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" />
          </label>
          <label>
            Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          <div style={{ textAlign: "right" }}>
            <Link to="/password-reset" style={{ fontSize: 12, color: "#64746f" }}>Forgot password?</Link>
          </div>
          {error ? <p className="error-text">{error}</p> : null}
          <button className="primary-button" disabled={loading}>{loading ? "Signing in" : "Sign in"}</button>
        </form>
        <p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }}>
          Don't have an account? <Link to="/signup" style={{ color: "#1d8a8a", fontWeight: 700 }}>Sign up</Link>
        </p>
      </section>
    </main>
  );
}
