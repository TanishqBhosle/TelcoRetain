import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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

interface FieldErrors {
  full_name?: string;
  email?: string;
  password?: string;
}

interface Touched {
  full_name?: boolean;
  email?: boolean;
  password?: boolean;
}

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("TIMEOUT")), ms)
    ),
  ]);
}

export function SignUpPage() {
  const navigate = useNavigate();
  const { setSession, setUser } = useAuthStore();
  const [full_name, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [touched, setTouched] = useState<Touched>({});

  function validateField(field: keyof FieldErrors, value: string): string {
    if (!value.trim()) {
      const labels: Record<keyof FieldErrors, string> = {
        full_name: "Full name",
        email: "Email",
        password: "Password",
      };
      return `${labels[field]} is required`;
    }
    if (field === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return "Please enter a valid email address";
    }
    return "";
  }

  function handleBlur(field: keyof FieldErrors) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const values: Record<keyof FieldErrors, string> = {
      full_name,
      email,
      password,
    };
    const errorMsg = validateField(field, values[field]);
    setFieldErrors((prev) => ({ ...prev, [field]: errorMsg }));
  }

  function validateAll(): boolean {
    const errors: FieldErrors = {
      full_name: validateField("full_name", full_name),
      email: validateField("email", email),
      password: validateField("password", password),
    };
    setFieldErrors(errors);
    setTouched({ full_name: true, email: true, password: true });
    return !errors.full_name && !errors.email && !errors.password;
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!validateAll()) return;

    setLoading(true);
    setError("");
    try {
      const registerPromise = api.post("/auth/register", {
        full_name,
        email,
        password,
        role_name: "Business Analyst",
      });

      await withTimeout(registerPromise, 15000);

      // Auto login immediately
      const tokens = await unwrap<TokenResponse>(api.post("/auth/login", { email, password }));
      setSession(tokens.access_token, tokens.refresh_token);
      const userObj = await unwrap<User>(api.get("/auth/me"));
      setUser(userObj);

      if (isAdminRole(userObj.role?.name)) {
        navigate("/admin/dashboard");
      } else {
        navigate("/app/dashboard");
      }
    } catch (err) {
      if (err instanceof Error && err.message === "TIMEOUT") {
        setError("Request timed out. Please try again.");
      } else {
        setError("Account created, but automatic sign in failed. Please try signing in manually.");
      }
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
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25, duration: 0.3 }}>
            Full Name
            <input
              value={full_name}
              onChange={(e) => setFullName(e.target.value)}
              onBlur={() => handleBlur("full_name")}
              type="text"
            />
            {touched.full_name && fieldErrors.full_name && (
              <span className="field-error">{fieldErrors.full_name}</span>
            )}
          </motion.label>
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3, duration: 0.3 }}>
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
          <motion.label initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35, duration: 0.3 }}>
            Password
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => handleBlur("password")}
              type="password"
              autoComplete="new-password"
            />
            {touched.password && fieldErrors.password && (
              <span className="field-error">{fieldErrors.password}</span>
            )}
          </motion.label>

          {error ? (
            <motion.p className="error-text" initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}>{error}</motion.p>
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
                Creating account
              </>
            ) : (
              "Create account"
            )}
          </motion.button>
        </form>
        <motion.p
          className="auth-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Already have an account? <Link to="/signin">Sign in</Link>
        </motion.p>
      </motion.section>
    </main>
  );
}
