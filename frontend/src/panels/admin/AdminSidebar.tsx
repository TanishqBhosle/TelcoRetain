import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Database,
  BrainCircuit,
  FileText,
  Cable,
} from "lucide-react";
import { SidebarGroup } from "../../components/SidebarGroup";

const adminNavGroups = [
  {
    label: "Overview",
    items: [
      { to: "/admin/dashboard", icon: LayoutDashboard, label: "Admin Dashboard" },
    ],
  },
  {
    label: "Management",
    items: [
      { to: "/admin/datasets", icon: Database, label: "Dataset Management" },
      { to: "/admin/models", icon: BrainCircuit, label: "Model Management" },
      { to: "/admin/users", icon: Users, label: "User Management" },
    ],
  },
  {
    label: "Security & Audit",
    items: [
      { to: "/admin/audit-logs", icon: FileText, label: "Audit Logs" },
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
      <div className="brand admin-brand">
        <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" style={{ height: "32px", width: "auto" }} />
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

