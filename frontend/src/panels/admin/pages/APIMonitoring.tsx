import { motion } from "framer-motion";
import { Wifi, Clock, AlertTriangle, CheckCircle, TrendingUp, BarChart3 } from "lucide-react";

export function APIMonitoring() {
  const metrics = [
    { label: "Total Requests", value: "12,456", icon: BarChart3, color: "#6366f1" },
    { label: "Avg Response Time", value: "145ms", icon: Clock, color: "#10b981" },
    { label: "Error Rate", value: "0.8%", icon: AlertTriangle, color: "#f59e0b" },
    { label: "Success Rate", value: "99.2%", icon: CheckCircle, color: "#10b981" },
  ];

  const endpoints = [
    { method: "GET", path: "/api/v1/customers", requests: 4521, avgTime: "120ms", errors: 12 },
    { method: "POST", path: "/api/v1/predictions/predict", requests: 2340, avgTime: "250ms", errors: 5 },
    { method: "GET", path: "/api/v1/dashboard/kpis", requests: 1890, avgTime: "85ms", errors: 2 },
    { method: "POST", path: "/api/v1/campaigns", requests: 890, avgTime: "180ms", errors: 8 },
    { method: "GET", path: "/api/v1/models", requests: 567, avgTime: "95ms", errors: 1 },
  ];

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">API Monitoring</h2>
        <p className="admin-page-subtitle">Monitor API performance and usage</p>
      </motion.div>

      <div className="admin-monitoring-grid">
        {metrics.map((metric, i) => (
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
          </motion.div>
        ))}
      </div>

      <motion.div
        className="admin-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <h3 className="admin-section-title">Top Endpoints</h3>
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Requests</th>
                <th>Avg Time</th>
                <th>Errors</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((ep, i) => (
                <tr key={i}>
                  <td>
                    <span className={`admin-method-badge ${ep.method.toLowerCase()}`}>
                      {ep.method}
                    </span>
                  </td>
                  <td className="admin-mono">{ep.path}</td>
                  <td>{ep.requests.toLocaleString()}</td>
                  <td>{ep.avgTime}</td>
                  <td>
                    <span className={ep.errors > 5 ? "admin-text-danger" : "admin-text-success"}>
                      {ep.errors}
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
