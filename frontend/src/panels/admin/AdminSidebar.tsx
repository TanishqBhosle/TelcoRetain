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
} from "lucide-react";
import { SidebarGroup } from "../../components/SidebarGroup";

const adminNavGroups = [
  {
    label: "Overview",
    items: [
      { to: "/admin/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    ],
  },
  {
    label: "Users & Access",
    items: [
      { to: "/admin/users", icon: Users, label: "User Management" },
      { to: "/admin/roles", icon: Shield, label: "Roles & Permissions" },
    ],
  },
  {
    label: "ML Platform",
    items: [
      { to: "/admin/datasets", icon: Database, label: "Dataset Management" },
      { to: "/admin/models", icon: BrainCircuit, label: "Model Registry" },
      { to: "/admin/model-monitoring", icon: Activity, label: "Model Monitoring" },
    ],
  },
  {
    label: "Infrastructure",
    items: [
      { to: "/admin/settings", icon: Settings, label: "System Settings" },
      { to: "/admin/api-monitoring", icon: Wifi, label: "API Monitoring" },
      { to: "/admin/database", icon: Server, label: "Database Health" },
      { to: "/admin/security", icon: Lock, label: "Security Center" },
    ],
  },
  {
    label: "Audit",
    items: [
      { to: "/admin/audit-logs", icon: FileText, label: "Audit Logs" },
      { to: "/admin/notifications", icon: Bell, label: "Notification Settings" },
    ],
  },
];

export function AdminSidebar() {
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
        {adminNavGroups.map((group) => (
          <SidebarGroup
            key={group.label}
            label={group.label}
            items={group.items}
          />
        ))}
      </nav>
    </motion.aside>
  );
}
