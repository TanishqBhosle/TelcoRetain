import { motion } from "framer-motion";
import { Server, Database, HardDrive, Activity, RefreshCw, AlertTriangle, CheckCircle } from "lucide-react";

export function DatabaseHealth() {
  const healthMetrics = [
    { label: "Status", value: "Healthy", icon: Activity, color: "#10b981", status: "good" },
    { label: "Connection Pool", value: "10/10", icon: Server, color: "#6366f1", status: "good" },
    { label: "Active Connections", value: "3", icon: Database, color: "#8b5cf6", status: "good" },
    { label: "Database Size", value: "256 MB", icon: HardDrive, color: "#f97316", status: "good" },
  ];

  const tables = [
    { name: "users", rows: 15, size: "12 KB" },
    { name: "roles", rows: 7, size: "4 KB" },
    { name: "permissions", rows: 25, size: "8 KB" },
    { name: "telecom_customers", rows: 5000, size: "2.5 MB" },
    { name: "churn_predictions", rows: 12500, size: "8.2 MB" },
    { name: "campaigns", rows: 45, size: "128 KB" },
    { name: "audit_logs", rows: 25000, size: "15.6 MB" },
    { name: "api_logs", rows: 50000, size: "32.1 MB" },
  ];

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="admin-page-header"
      >
        <div>
          <h2 className="admin-page-title">Database Health</h2>
          <p className="admin-page-subtitle">Monitor database performance and storage</p>
        </div>
        <button className="admin-btn secondary">
          <RefreshCw size={16} /> Refresh
        </button>
      </motion.div>

      <div className="admin-monitoring-grid">
        {healthMetrics.map((metric, i) => (
          <motion.div
            key={metric.label}
            className="admin-monitoring-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
          >
            <div className="admin-monitoring-icon" style={{ backgroundColor: `${metric.color}20`, color: metric.color }}>
              <metric.icon size={24} />
            </div>
            <div className="admin-monitoring-label">{metric.label}</div>
            <div className="admin-monitoring-value">{metric.value}</div>
            <div className={`admin-monitoring-status ${metric.status}`}>
              {metric.status === "good" ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="admin-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <h3 className="admin-section-title">Database Tables</h3>
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Table Name</th>
                <th>Rows</th>
                <th>Size</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((table, i) => (
                <tr key={i}>
                  <td className="admin-mono">{table.name}</td>
                  <td>{table.rows.toLocaleString()}</td>
                  <td>{table.size}</td>
                  <td>
                    <span className="admin-status active">
                      <CheckCircle size={12} /> Healthy
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
