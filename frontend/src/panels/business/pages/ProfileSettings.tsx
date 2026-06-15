import { motion } from "framer-motion";
import { User, Mail, Lock, Bell, Save, RefreshCw } from "lucide-react";
import { useAuthStore } from "../../../state/auth";

export function ProfileSettings() {
  const { user } = useAuthStore();

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Profile Settings</h2>
        <p className="business-page-subtitle">Manage your account settings and preferences</p>
      </motion.div>

      <div className="business-settings-grid">
        <motion.div
          className="business-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <div className="business-settings-header">
            <User size={24} />
            <h3>Personal Information</h3>
          </div>
          <div className="business-settings-content">
            <div className="business-form-group">
              <label>Full Name</label>
              <input type="text" defaultValue={user?.full_name || ""} />
            </div>
            <div className="business-form-group">
              <label>Email</label>
              <input type="email" defaultValue={user?.email || ""} disabled />
            </div>
            <div className="business-form-group">
              <label>Role</label>
              <input type="text" defaultValue={user?.role?.name || ""} disabled />
            </div>
          </div>
        </motion.div>

        <motion.div
          className="business-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div className="business-settings-header">
            <Lock size={24} />
            <h3>Change Password</h3>
          </div>
          <div className="business-settings-content">
            <div className="business-form-group">
              <label>Current Password</label>
              <input type="password" placeholder="Enter current password" />
            </div>
            <div className="business-form-group">
              <label>New Password</label>
              <input type="password" placeholder="Enter new password" />
            </div>
            <div className="business-form-group">
              <label>Confirm New Password</label>
              <input type="password" placeholder="Confirm new password" />
            </div>
          </div>
        </motion.div>

        <motion.div
          className="business-settings-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <div className="business-settings-header">
            <Bell size={24} />
            <h3>Notification Preferences</h3>
          </div>
          <div className="business-settings-content">
            <div className="business-form-group">
              <label className="business-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Email Notifications</span>
              </label>
            </div>
            <div className="business-form-group">
              <label className="business-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Campaign Updates</span>
              </label>
            </div>
            <div className="business-form-group">
              <label className="business-checkbox">
                <input type="checkbox" defaultChecked />
                <span>Customer Alerts</span>
              </label>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        className="business-settings-actions"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <button className="business-btn primary">
          <Save size={16} /> Save Changes
        </button>
        <button className="business-btn secondary">
          <RefreshCw size={16} /> Reset
        </button>
      </motion.div>
    </div>
  );
}
