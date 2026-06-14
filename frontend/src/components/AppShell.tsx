import { NavLink, Outlet, useNavigate } from "react-router-dom";
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
  { to: "/", icon: BarChart3, label: "Dashboard" },
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
  const { logout, user } = useAuthStore();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Cable size={24} />
          <span>Telco Retain</span>
        </div>
        <nav className="nav">
          {nav.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <strong>{user?.full_name ?? "Retention Team"}</strong>
            <span>{user?.role?.name ?? "Workspace"}</span>
          </div>
          <button
            className="icon-button"
            title="Log out"
            onClick={() => {
              logout();
              navigate("/signin");
            }}
          >
            <LogOut size={18} />
          </button>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
