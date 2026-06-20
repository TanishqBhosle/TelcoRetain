import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  User,
  BrainCircuit,
  Sparkles,
  BarChart3,
  Cable,
} from "lucide-react";
import { useAuthStore } from "../../state/auth";
import { SidebarGroup } from "../../components/SidebarGroup";

interface NavItem {
  to: string;
  icon: typeof LayoutDashboard;
  label: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const businessNavGroups: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { to: "/app/dashboard", icon: LayoutDashboard, label: "Dashboard" },
      { to: "/app/analytics", icon: BarChart3, label: "Analytics Dashboard" },
    ],
  },
  {
    label: "Customers",
    items: [
      { to: "/app/customers", icon: Users, label: "Customer Explorer" },
      { to: "/app/customers/1", icon: User, label: "Customer Profile" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { to: "/app/predict", icon: BrainCircuit, label: "Churn Prediction" },
      { to: "/app/shap", icon: BarChart3, label: "SHAP Analysis" },
      { to: "/app/recommendations", icon: Sparkles, label: "Recommendation Center" },
    ],
  },
];

export function BusinessSidebar() {
  const { user } = useAuthStore();

  return (
    <motion.aside
      className="business-sidebar"
      initial={{ x: -260, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="brand business-brand">
        <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" style={{ height: "32px", width: "auto" }} />
        <span className="business-badge">{user?.role?.name ?? "Business"}</span>
      </div>
      <nav className="business-nav">
        {businessNavGroups.map((group) => (
          <SidebarGroup
            key={group.label}
            label={group.label}
            items={group.items}
            itemClassName="business-nav-item"
          />
        ))}
      </nav>
    </motion.aside>
  );
}
