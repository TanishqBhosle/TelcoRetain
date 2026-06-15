import { motion } from "framer-motion";
import { Settings, Save, RefreshCw, Shield, Database, Bell } from "lucide-react";

export function SystemSettings() {
  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">System Settings</h2>
        <p className="admin-page-subtitle">Configure platform settings and preferences</p>
      </motion.div>

      <div className="admin-settings-grid">
        <motion.div
          className="admin-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <div className="admin-settings-header">
            <Settings size={24} />
            <h3>General Settings</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label>Platform Name</label>
              <input type="text" defaultValue="TelcoRetain" />
            </div>
            <div className="admin-form-group">
              <label>API Rate Limit (requests/minute)</label>
              <input type="number" defaultValue={120} />
            </div>
            <div className="admin-form-group">
              <label>Data Retention (days)</label>
              <input type="number" defaultValue={365} />
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Maintenance Mode</span>
              </label>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="admin-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div className="admin-settings-header">
            <Shield size={24} />
            <h3>Security Settings</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label>Minimum Password Length</label>
              <input type="number" defaultValue={8} />
            </div>
            <div className="admin-form-group">
              <label>Max Login Attempts</label>
              <input type="number" defaultValue={5} />
            </div>
            <div className="admin-form-group">
              <label>Lockout Duration (minutes)</label>
              <input type="number" defaultValue={15} />
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Require Email Verification</span>
              </label>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="admin-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <div className="admin-settings-header">
            <Database size={24} />
            <h3>Logging Settings</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Enable Audit Logging</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Enable API Logging</span>
              </label>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        className="admin-settings-actions"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <button className="admin-btn primary">
          <Save size={16} /> Save Settings
        </button>
        <button className="admin-btn secondary">
          <RefreshCw size={16} /> Reset to Defaults
        </button>
      </motion.div>
    </div>
  );
}
