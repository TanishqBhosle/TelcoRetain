import { motion } from "framer-motion";
import { Bell, Mail, MessageSquare, Webhook, Save, Plus, Trash2 } from "lucide-react";

export function NotificationSettings() {
  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="admin-page-title">Notification Settings</h2>
        <p className="admin-page-subtitle">Configure notification channels and preferences</p>
      </motion.div>

      <div className="admin-settings-grid">
        <motion.div
          className="admin-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <div className="admin-settings-header">
            <Mail size={24} />
            <h3>Email Notifications</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Enable Email Notifications</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label>Notification Email Addresses</label>
              <div className="admin-email-list">
                <div className="admin-email-item">
                  <span>admin@telco.com</span>
                  <button className="admin-icon-btn danger"><Trash2 size={14} /></button>
                </div>
                <div className="admin-email-item">
                  <span>ops@telco.com</span>
                  <button className="admin-icon-btn danger"><Trash2 size={14} /></button>
                </div>
              </div>
              <button className="admin-btn secondary small">
                <Plus size={14} /> Add Email
              </button>
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
            <MessageSquare size={24} />
            <h3>Slack Integration</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" />
                <span>Enable Slack Notifications</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label>Webhook URL</label>
              <input type="url" placeholder="https://hooks.slack.com/..." />
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
            <Bell size={24} />
            <h3>Notification Triggers</h3>
          </div>
          <div className="admin-settings-content">
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Model Retraining Complete</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Dataset Upload</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Security Events</span>
              </label>
            </div>
            <div className="admin-form-group">
              <label className="admin-checkbox">
                <input type="checkbox" defaultChecked />
                <span>System Errors</span>
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
      </motion.div>
    </div>
  );
}
