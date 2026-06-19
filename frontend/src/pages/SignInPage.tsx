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

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("TIMEOUT")), ms)
    ),
  ]);
}

export function SignInPage() {
  const navigate = useNavigate();
  const { accessToken, setSession, setUser } = useAuthStore();
  const [email, setEmail] = useState("admin@telecom-retention.com");
  const [password, setPassword] = useState("Admin@1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [touched, setTouched] = useState<{ email?: boolean; password?: boolean }>({});

  const currentUser = useAuthStore((s) => s.user);
  if (accessToken && currentUser) {
    const dest = isAdminRole(currentUser.role?.name) ? "/admin/dashboard" : "/app/dashboard";
    return <Navigate to={dest} replace />;
  }

  function validateField(field: "email" | "password", value: string) {
    if (!value.trim()) {
      return `${field === "email" ? "Email" : "Password"} is required`;
    }
    return "";
  }

  function handleBlur(field: "email" | "password") {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const value = field === "email" ? email : password;
    const errorMsg = validateField(field, value);
    setFieldErrors((prev) => ({ ...prev, [field]: errorMsg }));
  }

  function validateAll(): boolean {
    const emailErr = validateField("email", email);
    const passwordErr = validateField("password", password);
    setFieldErrors({ email: emailErr, password: passwordErr });
    setTouched({ email: true, password: true });
    return !emailErr && !passwordErr;
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!validateAll()) return;

    setLoading(true);
    setError("");
    try {
      const loginPromise = async () => {
        const tokens = await unwrap<TokenResponse>(api.post("/auth/login", { email, password }));
        setSession(tokens.access_token, tokens.refresh_token);
        const user = await unwrap<User>(api.get("/auth/me"));
        setUser(user);
        return user;
      };

      const user = await withTimeout(loginPromise(), 15000);

      if (isAdminRole(user.role?.name)) {
        navigate("/admin/dashboard");
      } else {
        navigate("/app/dashboard");
      }
    } catch (err) {
      if (err instanceof Error && err.message === "TIMEOUT") {
        setError("Request timed out. Please try again.");
      } else {
        setError("Sign in failed. Check credentials and backend availability.");
      }
      setPassword("");
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
        <form onSubmit={submit} className="form" noValidate>
          <motion.label
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.3 }}
          >
            Email
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={() => handleBlur("email")}
              type="email"
              autoComplete="email"
            />
            {touched.email && fieldErrors.email && (
              <span className="field-error">{fieldErrors.email}</span>
            )}
          </motion.label>
          <motion.label
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.35, duration: 0.3 }}
          >
            Password
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => handleBlur("password")}
              type="password"
              autoComplete="current-password"
            />
            {touched.password && fieldErrors.password && (
              <span className="field-error">{fieldErrors.password}</span>
            )}
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
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <span className="btn-spinner" aria-hidden="true" />
                Signing in
              </>
            ) : (
              "Sign in"
            )}
          </motion.button>
        </form>
        <motion.p
          className="auth-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Don't have an account? <Link to="/signup">Sign up</Link>
        </motion.p>
      </motion.section>
    </main>
  );
}
