import { motion } from "framer-motion";
import { Lock, Shield, AlertTriangle, CheckCircle, Key, Users, Clock } from "lucide-react";

export function SecurityCenter() {
  const securityMetrics = [
    { label: "Failed Logins (24h)", value: "12", icon: AlertTriangle, color: "#f59e0b" },
    { label: "Locked Accounts", value: "2", icon: Lock, color: "#ef4444" },
    { label: "Active Sessions", value: "8", icon: Users, color: "#6366f1" },
    { label: "2FA Enabled", value: "45%", icon: Shield, color: "#10b981" },
  ];

  const recentEvents = [
    { time: "2 min ago", event: "Failed login attempt", user: "user@example.com", ip: "192.168.1.100", severity: "warning" },
    { time: "15 min ago", event: "Password changed", user: "admin@telco.com", ip: "10.0.0.1", severity: "info" },
    { time: "1 hour ago", event: "Account locked", user: "test@example.com", ip: "172.16.0.50", severity: "error" },
    { time: "2 hours ago", event: "New device login", user: "manager@telco.com", ip: "192.168.2.200", severity: "info" },
  ];

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">Security Center</h2>
        <p className="admin-page-subtitle">Monitor security events and manage access controls</p>
      </motion.div>

      <div className="admin-monitoring-grid">
        {securityMetrics.map((metric, i) => (
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
        <h3 className="admin-section-title">Recent Security Events</h3>
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Event</th>
                <th>User</th>
                <th>IP Address</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event, i) => (
                <tr key={i}>
                  <td>
                    <div className="admin-event-time">
                      <Clock size={12} /> {event.time}
                    </div>
                  </td>
                  <td>{event.event}</td>
                  <td>{event.user}</td>
                  <td className="admin-mono">{event.ip}</td>
                  <td>
                    <span className={`admin-severity-badge ${event.severity}`}>
                      {event.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      <motion.div
        className="admin-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <h3 className="admin-section-title">Security Settings</h3>
        <div className="admin-settings-grid">
          <div className="admin-settings-card">
            <div className="admin-settings-header">
              <Key size={24} />
              <h3>Password Policy</h3>
            </div>
            <div className="admin-settings-content">
              <div className="admin-form-group">
                <label>Minimum Length</label>
                <input type="number" defaultValue={8} />
              </div>
              <div className="admin-form-group">
                <label className="admin-checkbox">
                  <input type="checkbox" defaultChecked />
                  <span>Require Uppercase</span>
                </label>
              </div>
              <div className="admin-form-group">
                <label className="admin-checkbox">
                  <input type="checkbox" defaultChecked />
                  <span>Require Numbers</span>
                </label>
              </div>
              <div className="admin-form-group">
                <label className="admin-checkbox">
                  <input type="checkbox" defaultChecked />
                  <span>Require Special Characters</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
