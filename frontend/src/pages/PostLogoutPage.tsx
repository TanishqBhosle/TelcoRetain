import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Cable, LogOut } from "lucide-react";

export function PostLogoutPage() {
  return (
    <main className="auth-screen">
      <motion.section
        className="auth-panel"
        style={{ textAlign: "center" }}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <motion.div
          className="brand auth-brand"
          style={{ justifyContent: "center" }}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Cable size={26} />
          <span>Telco Retain</span>
        </motion.div>
        <motion.div
          style={{ margin: "24px 0" }}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
        >
          <LogOut size={48} style={{ color: "#64746f" }} />
        </motion.div>
        <motion.h2
          style={{ marginBottom: 8 }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          You've been signed out
        </motion.h2>
        <motion.p
          style={{ color: "#64746f", fontSize: 14, marginBottom: 24 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Your session has been terminated securely. You can close this tab or sign in again.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Link
            to="/signin"
            className="primary-button"
            style={{ width: "100%", justifyContent: "center" }}
          >
            Sign in again
          </Link>
        </motion.div>
      </motion.section>
    </main>
  );
}
