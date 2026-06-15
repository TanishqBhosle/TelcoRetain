import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileText, Search, Download, Filter } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type AuditLog = {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
};

export function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    unwrap<{ items: AuditLog[] }>(api.get("/admin/audit-logs"))
      .then((data) => setLogs(data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filteredLogs = logs.filter(
    (log) =>
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.resource_type.toLowerCase().includes(search.toLowerCase())
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
          <h2 className="admin-page-title">Audit Logs</h2>
          <p className="admin-page-subtitle">Track all system and user actions</p>
        </div>
        <button className="admin-btn secondary">
          <Download size={16} /> Export Logs
        </button>
      </motion.div>

      <div className="admin-search-bar">
        <Search size={18} />
        <input
          type="text"
          placeholder="Search audit logs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button className="admin-filter-btn">
          <Filter size={16} /> Filter
        </button>
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
              <th>Timestamp</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Resource ID</th>
              <th>IP Address</th>
              <th>User Agent</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="admin-loading">Loading audit logs...</td>
              </tr>
            ) : filteredLogs.length === 0 ? (
              <tr>
                <td colSpan={6} className="admin-empty">No audit logs found</td>
              </tr>
            ) : (
              filteredLogs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>
                    <span className={`admin-action-badge ${log.action.toLowerCase()}`}>
                      {log.action}
                    </span>
                  </td>
                  <td>{log.resource_type}</td>
                  <td className="admin-mono">{log.resource_id?.slice(0, 8)}...</td>
                  <td className="admin-mono">{log.ip_address}</td>
                  <td className="admin-truncate">{log.user_agent}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
