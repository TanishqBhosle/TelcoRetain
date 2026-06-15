import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Shield,
  Database,
  BrainCircuit,
  Activity,
  Settings,
  FileText,
  Wifi,
  Server,
  Lock,
  Bell,
  Cable,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "../../state/auth";

const adminNav = [
  { to: "/admin/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/admin/users", icon: Users, label: "User Management" },
  { to: "/admin/roles", icon: Shield, label: "Roles & Permissions" },
  { to: "/admin/datasets", icon: Database, label: "Dataset Management" },
  { to: "/admin/models", icon: BrainCircuit, label: "Model Registry" },
  { to: "/admin/model-monitoring", icon: Activity, label: "Model Monitoring" },
  { to: "/admin/settings", icon: Settings, label: "System Settings" },
  { to: "/admin/audit-logs", icon: FileText, label: "Audit Logs" },
  { to: "/admin/api-monitoring", icon: Wifi, label: "API Monitoring" },
  { to: "/admin/database", icon: Server, label: "Database Health" },
  { to: "/admin/security", icon: Lock, label: "Security Center" },
  { to: "/admin/notifications", icon: Bell, label: "Notification Settings" },
];

export function AdminSidebar() {
  const location = useLocation();

  return (
    <motion.aside
      className="admin-sidebar"
      initial={{ x: -260, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="admin-brand">
        <Cable size={24} />
        <span>Telco Retain</span>
        <span className="admin-badge">Admin</span>
      </div>
      <nav className="admin-nav">
        {adminNav.map((item, i) => (
          <motion.div
            key={item.to}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.04, duration: 0.3 }}
          >
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `admin-nav-item ${isActive ? "active" : ""}`
              }
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          </motion.div>
        ))}
      </nav>
    </motion.aside>
  );
}
