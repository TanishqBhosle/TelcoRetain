import { FormEvent, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Cable, CheckCircle } from "lucide-react";
import { api, unwrap } from "../lib/api";

export function PasswordResetConfirmPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (!token) {
      setError("No reset token provided.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await unwrap<null>(api.post("/auth/password-reset/confirm", { token, new_password: password }));
      setSuccess(true);
    } catch {
      setError("Failed to reset password. The token may be invalid or expired.");
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
        {success ? (
          <>
            <CheckCircle size={48} color="#146b45" style={{ margin: "16px auto", display: "block" }} />
            <p style={{ color: "#146b45", fontSize: 14, textAlign: "center" }}>Password reset successfully!</p>
            <Link to="/signin" style={{ display: "block", textAlign: "center", marginTop: 16, color: "#1d8a8a", fontWeight: 700 }}>
              Sign in with new password
            </Link>
          </>
        ) : (
          <>
            <h2 style={{ margin: "0 0 18px", fontSize: 18 }}>Set New Password</h2>
            <form onSubmit={submit} className="form">
              <label>
                New Password
                <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" autoComplete="new-password" minLength={8} required />
              </label>
              <label>
                Confirm Password
                <input value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} type="password" autoComplete="new-password" minLength={8} required />
              </label>
              {error && <p className="error-text">{error}</p>}
              <button className="primary-button" disabled={loading}>{loading ? "Resetting..." : "Reset password"}</button>
            </form>
          </>
        )}
      </section>
    </main>
  );
}
