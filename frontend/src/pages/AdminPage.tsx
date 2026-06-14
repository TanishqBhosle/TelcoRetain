import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Shield } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { StatusPill } from "../components/StatusPill";
import { api, unwrap } from "../lib/api";

type Health = {
  status: string;
  database_connected: boolean;
  redis_connected: boolean;
  ml_models_loaded: boolean;
  uptime_seconds: number;
};

type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  email_verified: boolean;
  role?: { name: string };
};

export function AdminPage() {
  const [health, setHealth] = useState<Health | null>(null);
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    void Promise.all([
      unwrap<Health>(api.get("/admin/system-health")).then(setHealth).catch(() => setHealth(null)),
      unwrap<User[]>(api.get("/admin/users")).then(setUsers).catch(() => setUsers([]))
    ]);
  }, []);

  return (
    <section className="page">
      <div className="page-title">
        <h1>Admin</h1>
        <Link to="/admin/audit-logs" className="primary-button" style={{ textDecoration: "none", fontSize: 13 }}>
          <Shield size={14} /> Audit Logs
        </Link>
      </div>
      <div className="metric-grid compact-metrics">
        <MetricCard label="System" value={health?.status ?? "unknown"} />
        <MetricCard label="Database" value={health?.database_connected ? "online" : "offline"} />
        <MetricCard label="Redis" value={health?.redis_connected ? "online" : "optional"} />
        <MetricCard label="ML" value={health?.ml_models_loaded ? "loaded" : "degraded"} />
      </div>
      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Email</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td><strong>{user.full_name}</strong></td>
                <td>{user.role?.name ?? "-"}</td>
                <td>{user.email}</td>
                <td><StatusPill value={user.is_active ? "Active" : "Inactive"} /></td>
              </tr>
            ))}
            {!users.length ? <tr><td colSpan={4} className="empty">No users found</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
