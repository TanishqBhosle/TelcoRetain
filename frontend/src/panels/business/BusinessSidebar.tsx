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
    label: "Analytics",
    items: [
      { to: "/app/dashboard", icon: LayoutDashboard, label: "Dashboard" },
      { to: "/app/analytics", icon: BarChart3, label: "Analytics Dashboard" },
      { to: "/app/reports", icon: FileBarChart, label: "Reports" },
    ],
  },
  {
    label: "Customers",
    items: [
      { to: "/app/customers", icon: Users, label: "Customer Explorer" },
      { to: "/app/predict", icon: BrainCircuit, label: "Churn Prediction" },
      { to: "/app/explain", icon: Lightbulb, label: "Explainable AI" },
    ],
  },
  {
    label: "Management",
    items: [
      { to: "/app/recommendations", icon: Sparkles, label: "Recommendation Center" },
      { to: "/app/campaigns", icon: Megaphone, label: "Campaign Management" },
    ],
  },
  {
    label: "Settings",
    items: [
      { to: "/app/settings", icon: Settings, label: "Profile Settings" },
    ],
  },
];

export function BusinessSidebar() {
  const { user } = useAuthStore();

  const role = user?.role?.name;

  const allowedRoutes = (() => {
    if (!role) return [];

    if (role === "Customer Support Executive") {
      return ["/app/dashboard", "/app/customers", "/app/predict", "/app/recommendations", "/app/settings"];
    }
    if (role === "Executive Viewer") {
      return ["/app/dashboard", "/app/reports", "/app/analytics", "/app/settings"];
    }
    if (role === "Business Analyst") {
      return ["/app/dashboard", "/app/customers", "/app/analytics", "/app/reports", "/app/settings"];
    }
    if (role === "Marketing Manager") {
      return ["/app/dashboard", "/app/campaigns", "/app/recommendations", "/app/analytics", "/app/settings"];
    }
    return null; // null means all routes allowed
  })();

  const filteredGroups = businessNavGroups
    .map((group) => ({
      ...group,
      items: allowedRoutes === null
        ? group.items
        : group.items.filter((item) => allowedRoutes.includes(item.to)),
    }))
    .filter((group) => group.items.length > 0);

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
        {filteredGroups.map((group) => (
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
