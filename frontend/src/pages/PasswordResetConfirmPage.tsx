import { FormEvent, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
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
      <motion.section
        className="auth-panel"
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div className="brand auth-brand" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Cable size={26} />
          <span>Telco Retain</span>
        </motion.div>
        {success ? (
          <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: "spring", stiffness: 200 }}>
            <CheckCircle size={48} color="#146b45" style={{ margin: "16px auto", display: "block" }} />
            <p style={{ color: "#146b45", fontSize: 14, textAlign: "center" }}>Password reset successfully!</p>
            <Link to="/signin" style={{ display: "block", textAlign: "center", marginTop: 16, color: "#1d8a8a", fontWeight: 700 }}>
              Sign in with new password
            </Link>
          </motion.div>
        ) : (
          <>
            <motion.h2 style={{ margin: "0 0 18px", fontSize: 18 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>Set New Password</motion.h2>
            <form onSubmit={submit} className="form">
              <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}>
                New Password
                <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" autoComplete="new-password" minLength={8} required />
              </motion.label>
              <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
                Confirm Password
                <input value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} type="password" autoComplete="new-password" minLength={8} required />
              </motion.label>
              {error && <motion.p className="error-text" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{error}</motion.p>}
              <motion.button className="primary-button" disabled={loading} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
                {loading ? "Resetting..." : "Reset password"}
              </motion.button>
            </form>
          </>
        )}
      </motion.section>
    </main>
  );
}
