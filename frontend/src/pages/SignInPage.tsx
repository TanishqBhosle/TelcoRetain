import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api, unwrap } from "../lib/api";
import { useAuthStore } from "../state/auth";
import { isAdminRole } from "../components/RoleGuard";

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

  const currentUser = useAuthStore((s) => s.user);
  if (accessToken && currentUser) {
    const dest = isAdminRole(currentUser.role?.name) ? "/admin/dashboard" : "/app/dashboard";
    return <Navigate to={dest} replace />;
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const tokens = await unwrap<TokenResponse>(api.post("/auth/login", { email, password }));
      setSession(tokens.access_token, tokens.refresh_token);
      const user = await unwrap<User>(api.get("/auth/me"));
      setUser(user);

      if (isAdminRole(user.role?.name)) {
        navigate("/admin/dashboard");
      } else {
        navigate("/app/dashboard");
      }
    } catch {
      setError("Sign in failed. Check credentials and backend availability.");
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
          <motion.label
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.3 }}
          >
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" />
          </motion.label>
          <motion.label
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.35, duration: 0.3 }}
          >
            Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </motion.label>
          <div style={{ textAlign: "right" }}>
            <Link to="/password-reset" style={{ fontSize: 12, color: "#64746f" }}>Forgot password?</Link>
          </div>
          {error ? (
            <motion.p
              className="error-text"
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {error}
            </motion.p>
          ) : null}
          <motion.button
            className="primary-button"
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? "Signing in" : "Sign in"}
          </motion.button>
        </form>
        <motion.p
          style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#64746f" }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Don't have an account? <Link to="/signup" style={{ color: "#1d8a8a", fontWeight: 700 }}>Sign up</Link>
        </motion.p>
      </motion.section>
    </main>
  );
}
