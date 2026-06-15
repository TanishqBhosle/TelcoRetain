import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Activity,
  Database,
  BrainCircuit,
  Shield,
  Server,
  Cpu,
  HardDrive,
} from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type SystemHealth = {
  status: string;
  database_connected: boolean;
  redis_connected: boolean;
  ml_models_loaded: boolean;
  uptime_seconds: number;
  system_metrics: Record<string, any>;
};

type AdminKPI = {
  label: string;
  value: string | number;
  icon: any;
  color: string;
};

export function AdminDashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<SystemHealth>(api.get("/admin/system-health"))
      .then(setHealth)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const kpis: AdminKPI[] = [
    { label: "System Status", value: health?.status ?? "Loading...", icon: Activity, color: "#10b981" },
    { label: "Database", value: health?.database_connected ? "Connected" : "Disconnected", icon: Database, color: health?.database_connected ? "#10b981" : "#ef4444" },
    { label: "Redis Cache", value: health?.redis_connected ? "Connected" : "Disconnected", icon: Server, color: health?.redis_connected ? "#10b981" : "#ef4444" },
    { label: "ML Models", value: health?.ml_models_loaded ? "Loaded" : "Not Loaded", icon: BrainCircuit, color: health?.ml_models_loaded ? "#10b981" : "#f59e0b" },
    { label: "Uptime", value: `${Math.floor((health?.uptime_seconds ?? 0) / 3600)}h ${Math.floor(((health?.uptime_seconds ?? 0) % 3600) / 60)}m`, icon: Cpu, color: "#6366f1" },
    { label: "CPU Usage", value: `${health?.system_metrics?.cpu_percent ?? 0}%`, icon: Cpu, color: "#8b5cf6" },
    { label: "Memory Usage", value: `${health?.system_metrics?.memory_percent ?? 0}%`, icon: HardDrive, color: "#ec4899" },
    { label: "Disk Usage", value: `${health?.system_metrics?.disk_percent ?? 0}%`, icon: HardDrive, color: "#f97316" },
  ];

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">System Dashboard</h2>
        <p className="admin-page-subtitle">Monitor platform health and system metrics</p>
      </motion.div>

      <div className="admin-kpi-grid">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.label}
            className="admin-kpi-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
          >
            <div className="admin-kpi-icon" style={{ backgroundColor: `${kpi.color}20`, color: kpi.color }}>
              <kpi.icon size={24} />
            </div>
            <div className="admin-kpi-content">
              <span className="admin-kpi-label">{kpi.label}</span>
              <span className="admin-kpi-value">{loading ? "..." : kpi.value}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="admin-section">
        <h3 className="admin-section-title">Quick Actions</h3>
        <div className="admin-actions-grid">
          <a href="/admin/users" className="admin-action-card">
            <Users size={24} />
            <span>Manage Users</span>
          </a>
          <a href="/admin/roles" className="admin-action-card">
            <Shield size={24} />
            <span>Roles & Permissions</span>
          </a>
          <a href="/admin/models" className="admin-action-card">
            <BrainCircuit size={24} />
            <span>Model Registry</span>
          </a>
          <a href="/admin/audit-logs" className="admin-action-card">
            <Activity size={24} />
            <span>Audit Logs</span>
          </a>
        </div>
      </div>
    </div>
  );
}
