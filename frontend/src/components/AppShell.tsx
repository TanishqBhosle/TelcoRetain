import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart3,
  BrainCircuit,
  Cable,
  FileBarChart,
  LogOut,
  Megaphone,
  MonitorCog,
  Shield,
  Sparkles,
  Users
} from "lucide-react";
import { useAuthStore } from "../state/auth";

const nav = [
  { to: "/dashboard", icon: BarChart3, label: "Dashboard" },
  { to: "/customers", icon: Users, label: "Customers" },
  { to: "/predict", icon: BrainCircuit, label: "Prediction" },
  { to: "/recommendations", icon: Sparkles, label: "Offers" },
  { to: "/campaigns", icon: Megaphone, label: "Campaigns" },
  { to: "/analytics", icon: FileBarChart, label: "Analytics" },
  { to: "/models", icon: MonitorCog, label: "Models" },
  { to: "/admin", icon: Shield, label: "Admin" }
];

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuthStore();

  return (
    <div className="shell">
      <motion.aside
        className="sidebar"
        initial={{ x: -244, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <div className="brand">
          <Cable size={24} />
          <span>Telco Retain</span>
        </div>
        <nav className="nav">
          {nav.map((item, i) => (
            <motion.div
              key={item.to}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + i * 0.04, duration: 0.3 }}
            >
              <NavLink
                to={item.to}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            </motion.div>
          ))}
        </nav>
      </motion.aside>
      <main className="main">
        <motion.header
          className="topbar"
          initial={{ y: -64, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div>
            <strong>{user?.full_name ?? "Retention Team"}</strong>
            <span>{user?.role?.name ?? "Workspace"}</span>
          </div>
          <motion.button
            className="icon-button"
            title="Log out"
            onClick={() => {
              logout();
              navigate("/post-logout");
            }}
            whileHover={{ scale: 1.1, backgroundColor: "#ffe3e7" }}
            whileTap={{ scale: 0.9 }}
          >
            <LogOut size={18} />
          </motion.button>
        </motion.header>
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
