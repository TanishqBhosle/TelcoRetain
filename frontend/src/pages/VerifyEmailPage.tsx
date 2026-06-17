import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle, XCircle } from "lucide-react";
import { api, unwrap } from "../lib/api";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided.");
      return;
    }
    void unwrap<null>(api.get(`/auth/verify-email`, { params: { token } }))
      .then(() => {
        setStatus("success");
        setMessage("Email verified successfully! You can now sign in.");
      })
      .catch(() => {
        setStatus("error");
        setMessage("Invalid or expired verification token.");
      });
  }, [token]);

  return (
    <main className="auth-screen">
      <motion.section
        className="auth-panel"
        style={{ textAlign: "center" }}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div className="brand auth-brand" style={{ justifyContent: "center" }} initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" />
        </motion.div>
        {status === "loading" && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Verifying your email...</motion.p>}
        {status === "success" && (
          <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: "spring", stiffness: 200 }}>
            <CheckCircle size={48} color="#146b45" style={{ margin: "16px auto" }} />
            <p style={{ color: "#146b45", fontSize: 14 }}>{message}</p>
          </motion.div>
        )}
        {status === "error" && (
          <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: "spring", stiffness: 200 }}>
            <XCircle size={48} color="#9d2340" style={{ margin: "16px auto" }} />
            <p className="error-text">{message}</p>
          </motion.div>
        )}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Link to="/signin" style={{ display: "inline-block", marginTop: 16, color: "#1d8a8a", fontWeight: 700, fontSize: 14 }}>
            Go to Sign In
          </Link>
        </motion.div>
      </motion.section>
    </main>
  );
}
