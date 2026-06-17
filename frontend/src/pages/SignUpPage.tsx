import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api, unwrap } from "../lib/api";

export function SignUpPage() {
  const navigate = useNavigate();
  const [full_name, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [gender, setGender] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.post("/auth/register", { full_name, email, password, gender: gender || undefined, role_name: "Business Analyst" });
      navigate("/signin");
    } catch {
      setError("Registration failed. Email may already be in use.");
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
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <motion.div
          className="brand auth-brand"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" />
        </motion.div>
        <form onSubmit={submit} className="form">
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25, duration: 0.3 }}>
            Full Name
            <input value={full_name} onChange={(e) => setFullName(e.target.value)} type="text" required />
          </motion.label>
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3, duration: 0.3 }}>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required autoComplete="email" />
          </motion.label>
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35, duration: 0.3 }}>
            Password
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required autoComplete="new-password" />
          </motion.label>
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4, duration: 0.3 }}>
            Gender (optional)
            <select value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="">Prefer not to say</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </motion.label>
          {error ? (
            <motion.p className="error-text" initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}>{error}</motion.p>
          ) : null}
          <motion.button
            className="primary-button"
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? "Creating account" : "Create account"}
          </motion.button>
        </form>
        <motion.p
          style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Already have an account? <Link to="/signin" style={{ color: "#1d8a8a", fontWeight: 700 }}>Sign in</Link>
        </motion.p>
      </motion.section>
    </main>
  );
}
