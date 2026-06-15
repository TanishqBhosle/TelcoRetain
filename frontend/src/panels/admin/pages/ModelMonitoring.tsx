import { motion } from "framer-motion";
import { Activity, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from "lucide-react";

export function ModelMonitoring() {
  const metrics = [
    { label: "Model Accuracy", value: "94.2%", trend: "+2.1%", status: "good" },
    { label: "AUC Score", value: "0.912", trend: "+0.015", status: "good" },
    { label: "Precision", value: "89.5%", trend: "-0.3%", status: "warning" },
    { label: "Recall", value: "91.8%", trend: "+1.2%", status: "good" },
    { label: "F1 Score", value: "90.6%", trend: "+0.5%", status: "good" },
    { label: "Drift Detected", value: "No", trend: "Stable", status: "good" },
  ];

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">Model Monitoring</h2>
        <p className="admin-page-subtitle">Track model performance and detect drift</p>
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
            <div className="admin-monitoring-header">
              <span className="admin-monitoring-label">{metric.label}</span>
              <span className={`admin-monitoring-status ${metric.status}`}>
                {metric.status === "good" ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
              </span>
            </div>
            <div className="admin-monitoring-value">{metric.value}</div>
            <div className={`admin-monitoring-trend ${metric.trend.startsWith("+") ? "positive" : metric.trend.startsWith("-") ? "negative" : "neutral"}`}>
              {metric.trend.startsWith("+") ? <TrendingUp size={14} /> : metric.trend.startsWith("-") ? <TrendingDown size={14} /> : null}
              {metric.trend}
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
        <h3 className="admin-section-title">Recent Performance Logs</h3>
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Model</th>
                <th>Accuracy</th>
                <th>AUC</th>
                <th>Sample Size</th>
                <th>Drift</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={6} className="admin-empty">No performance logs available</td>
              </tr>
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
