import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Shield, Plus, Edit, Trash2, Check, X } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type Permission = {
  id: string;
  permission_name: string;
  description: string;
};

type Role = {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
};

export function RolesPermissions() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<Role[]>(api.get("/admin/roles"))
      .then(setRoles)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const allPermissions = [
    "users:create", "users:read", "users:update", "users:delete",
    "roles:manage", "models:read", "models:write", "models:retrain", "models:activate",
    "datasets:read", "datasets:write", "audit:read", "system:settings", "system:health",
    "customers:read", "predictions:read", "predictions:write",
    "campaigns:read", "campaigns:write", "recommendations:read", "recommendations:write",
    "analytics:read", "reports:read", "reports:export", "dashboard:read",
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
          <h2 className="admin-page-title">Roles & Permissions</h2>
          <p className="admin-page-subtitle">Manage system roles and their permissions</p>
        </div>
        <button className="admin-btn primary">
          <Plus size={16} /> Add Role
        </button>
      </motion.div>

      <div className="admin-roles-grid">
        {loading ? (
          <div className="admin-loading">Loading roles...</div>
        ) : (
          roles.map((role, i) => (
            <motion.div
              key={role.id}
              className="admin-role-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="admin-role-header">
                <Shield size={24} />
                <div>
                  <h3>{role.name}</h3>
                  <p>{role.description}</p>
                </div>
                <div className="admin-role-actions">
                  <button className="admin-icon-btn" title="Edit">
                    <Edit size={16} />
                  </button>
                  <button className="admin-icon-btn danger" title="Delete">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <div className="admin-role-permissions">
                <h4>Permissions ({role.permissions.length})</h4>
                <div className="admin-permission-tags">
                  {role.permissions.map((perm) => (
                    <span key={perm.id} className="admin-permission-tag">
                      {perm.permission_name}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
