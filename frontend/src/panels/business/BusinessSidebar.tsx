import { NavLink, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  BrainCircuit,
  Lightbulb,
  Sparkles,
  Megaphone,
  BarChart3,
  FileBarChart,
  Settings,
  Cable,
} from "lucide-react";
import { useAuthStore } from "../../state/auth";

const businessNav = [
  { to: "/app/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/app/customers", icon: Users, label: "Customer Explorer" },
  { to: "/app/predict", icon: BrainCircuit, label: "Churn Prediction" },
  { to: "/app/explain", icon: Lightbulb, label: "Explainable AI" },
  { to: "/app/recommendations", icon: Sparkles, label: "Recommendation Center" },
  { to: "/app/campaigns", icon: Megaphone, label: "Campaign Management" },
  { to: "/app/analytics", icon: BarChart3, label: "Analytics Dashboard" },
  { to: "/app/reports", icon: FileBarChart, label: "Reports" },
  { to: "/app/settings", icon: Settings, label: "Profile Settings" },
];

export function BusinessSidebar() {
  const location = useLocation();
  const { user } = useAuthStore();

  const filteredNav = businessNav.filter((item) => {
    const role = user?.role?.name;
    if (!role) return false;

    if (role === "Customer Support Executive") {
      return ["/app/dashboard", "/app/customers", "/app/predict", "/app/recommendations", "/app/settings"].includes(item.to);
    }
    if (role === "Executive Viewer") {
      return ["/app/dashboard", "/app/reports", "/app/analytics", "/app/settings"].includes(item.to);
    }
    if (role === "Business Analyst") {
      return ["/app/dashboard", "/app/customers", "/app/analytics", "/app/reports", "/app/settings"].includes(item.to);
    }
    if (role === "Marketing Manager") {
      return ["/app/dashboard", "/app/campaigns", "/app/recommendations", "/app/analytics", "/app/settings"].includes(item.to);
    }
    return true;
  });

  return (
    <motion.aside
      className="business-sidebar"
      initial={{ x: -260, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="business-brand">
        <Cable size={24} />
        <span>Telco Retain</span>
        <span className="business-badge">{user?.role?.name ?? "Business"}</span>
      </div>
      <nav className="business-nav">
        {filteredNav.map((item, i) => (
          <motion.div
            key={item.to}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.04, duration: 0.3 }}
          >
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `business-nav-item ${isActive ? "active" : ""}`
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
