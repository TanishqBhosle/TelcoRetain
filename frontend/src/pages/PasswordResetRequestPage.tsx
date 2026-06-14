import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Cable } from "lucide-react";
import { api, unwrap } from "../lib/api";

export function PasswordResetRequestPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await unwrap<string>(api.post("/auth/password-reset/request", { email }));
      setSuccess("If an account exists with that email, reset instructions have been sent.");
    } catch {
      setError("Failed to request password reset. Please try again.");
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
        <h2 style={{ margin: "0 0 18px", fontSize: 18 }}>Reset Password</h2>
        <p style={{ color: "#64746f", fontSize: 13, marginTop: 0, marginBottom: 14 }}>
          Enter your email address and we'll send you a link to reset your password.
        </p>
        <form onSubmit={submit} className="form">
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
          </label>
          {error && <p className="error-text">{error}</p>}
          {success && <p style={{ color: "#146b45", fontSize: 13, margin: 0 }}>{success}</p>}
          <button className="primary-button" disabled={loading}>{loading ? "Sending..." : "Send reset link"}</button>
        </form>
        <p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }}>
          <Link to="/signin" style={{ color: "#1d8a8a", fontWeight: 700 }}>Back to Sign in</Link>
        </p>
      </section>
    </main>
  );
}
