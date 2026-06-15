import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, Plus, Edit, Trash2, Search } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  role?: { name: string; id: string };
};

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    unwrap<User[]>(api.get("/admin/users"))
      .then(setUsers)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filteredUsers = users.filter(
    (u) =>
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="admin-page-header"
      >
        <div>
          <h2 className="admin-page-title">User Management</h2>
          <p className="admin-page-subtitle">Manage platform users and their roles</p>
        </div>
        <button className="admin-btn primary">
          <Plus size={16} /> Add User
        </button>
      </motion.div>

      <div className="admin-search-bar">
        <Search size={18} />
        <input
          type="text"
          placeholder="Search users by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <motion.div
        className="admin-table-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
      >
        <table className="admin-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Verified</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="admin-loading">Loading users...</td>
              </tr>
            ) : filteredUsers.length === 0 ? (
              <tr>
                <td colSpan={6} className="admin-empty">No users found</td>
              </tr>
            ) : (
              filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td>
                    <div className="admin-user-cell">
                      <div className="admin-avatar">{user.full_name.charAt(0)}</div>
                      <span>{user.full_name}</span>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span className="admin-role-badge">{user.role?.name ?? "N/A"}</span>
                  </td>
                  <td>
                    <span className={`admin-status ${user.is_active ? "active" : "inactive"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td>
                    <span className={`admin-status ${user.email_verified ? "verified" : "unverified"}`}>
                      {user.email_verified ? "Yes" : "No"}
                    </span>
                  </td>
                  <td>
                    <div className="admin-actions">
                      <button className="admin-icon-btn" title="Edit">
                        <Edit size={16} />
                      </button>
                      <button className="admin-icon-btn danger" title="Delete">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
