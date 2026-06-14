import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
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
        <motion.h2 style={{ margin: "0 0 18px", fontSize: 18 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>Reset Password</motion.h2>
        <motion.p style={{ color: "#64746f", fontSize: 13, marginTop: 0, marginBottom: 14 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}>
          Enter your email address and we'll send you a link to reset your password.
        </motion.p>
        <form onSubmit={submit} className="form">
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
          </motion.label>
          {error && <motion.p className="error-text" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{error}</motion.p>}
          {success && <motion.p style={{ color: "#146b45", fontSize: 13, margin: 0 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{success}</motion.p>}
          <motion.button className="primary-button" disabled={loading} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
            {loading ? "Sending..." : "Send reset link"}
          </motion.button>
        </form>
        <motion.p style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <Link to="/signin" style={{ color: "#1d8a8a", fontWeight: 700 }}>Back to Sign in</Link>
        </motion.p>
      </motion.section>
    </main>
  );
}
