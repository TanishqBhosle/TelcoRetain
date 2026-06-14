import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Cable, CheckCircle, XCircle } from "lucide-react";
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
      <section className="auth-panel" style={{ textAlign: "center" }}>
        <div className="brand auth-brand" style={{ justifyContent: "center" }}>
          <Cable size={26} />
          <span>Telco Retain</span>
        </div>
        {status === "loading" && <p>Verifying your email...</p>}
        {status === "success" && (
          <>
            <CheckCircle size={48} color="#146b45" style={{ margin: "16px auto" }} />
            <p style={{ color: "#146b45", fontSize: 14 }}>{message}</p>
          </>
        )}
        {status === "error" && (
          <>
            <XCircle size={48} color="#9d2340" style={{ margin: "16px auto" }} />
            <p className="error-text">{message}</p>
          </>
        )}
        <Link to="/signin" style={{ display: "inline-block", marginTop: 16, color: "#1d8a8a", fontWeight: 700, fontSize: 14 }}>
          Go to Sign In
        </Link>
      </section>
    </main>
  );
}
