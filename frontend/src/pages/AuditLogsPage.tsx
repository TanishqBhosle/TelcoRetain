import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileText, Filter } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { FadeIn, StaggerContainer, staggerItem } from "../components/animations";
import { api, unwrap } from "../lib/api";

type AuditLog = {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  response_status?: number;
  created_at: string;
};

type ApiLog = {
  id: string;
  user_id?: string;
  endpoint: string;
  method: string;
  response_status: number;
  response_time_ms?: number;
  ip_address?: string;
  error_message?: string;
  created_at: string;
};

type Paginated<T> = { items: T[]; total: number; page: number; limit: number; pages: number };

export function AuditLogsPage() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [apiLogs, setApiLogs] = useState<ApiLog[]>([]);
  const [activeTab, setActiveTab] = useState<"audit" | "api">("audit");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");
  const limit = 30;

  useEffect(() => {
    if (activeTab === "audit") {
      const params: Record<string, string | number> = { page, limit };
      if (actionFilter) params.action = actionFilter;
      if (resourceFilter) params.resource_type = resourceFilter;
      void unwrap<Paginated<AuditLog>>(api.get("/admin/audit-logs", { params }))
        .then((data) => {
          setAuditLogs(data.items);
          setTotal(data.total);
        })
        .catch(() => {
          setAuditLogs([]);
          setTotal(0);
        });
    } else {
      void unwrap<ApiLog[]>(api.get("/admin/api-logs", { params: { page, limit } }))
        .then(setApiLogs)
        .catch(() => setApiLogs([]));
    }
  }, [activeTab, page, actionFilter, resourceFilter]);

  const totalPages = Math.ceil(total / limit);

  return (
    <section className="page">
      <FadeIn>
        <div className="page-title">
          <h1>Audit Logs</h1>
          <FileText size={24} />
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <div style={{ display: "flex", gap: 4, borderBottom: "1px solid #dbe5df", marginBottom: 0 }}>
          {(["audit", "api"] as const).map((tab) => (
            <motion.button
              key={tab}
              onClick={() => { setActiveTab(tab); setPage(1); }}
              whileHover={{ backgroundColor: activeTab === tab ? "#1d8a8a" : "#e8eee9" }}
              whileTap={{ scale: 0.97 }}
              style={{
                padding: "10px 16px",
                border: "none",
                background: activeTab === tab ? "#1d8a8a" : "transparent",
                color: activeTab === tab ? "#fff" : "#64746f",
                fontWeight: 700,
                fontSize: 13,
                cursor: "pointer",
                borderRadius: "8px 8px 0 0",
              }}
            >
              {tab === "audit" ? "User Actions" : "API Transactions"}
            </motion.button>
          ))}
        </div>
      </FadeIn>

      {activeTab === "audit" && (
        <FadeIn delay={0.2}>
          <div className="panel">
            <div style={{ display: "flex", gap: 12, padding: "12px 16px", borderBottom: "1px solid #dbe5df", alignItems: "center" }}>
              <Filter size={14} color="#64746f" />
              <input
                value={actionFilter}
                onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
                placeholder="Filter by action"
                style={{ width: 160, minHeight: 32, fontSize: 12 }}
              />
              <input
                value={resourceFilter}
                onChange={(e) => { setResourceFilter(e.target.value); setPage(1); }}
                placeholder="Filter by resource"
                style={{ width: 160, minHeight: 32, fontSize: 12 }}
              />
              <span style={{ fontSize: 12, color: "#64746f" }}>{total} records</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Resource ID</th>
                  <th>IP Address</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <StaggerContainer stagger={0.03}>
                  {auditLogs.map((log) => (
                    <motion.tr key={log.id} variants={staggerItem}>
                      <td style={{ fontSize: 12, whiteSpace: "nowrap" }}>{log.created_at}</td>
                      <td><StatusPill value={log.action} /></td>
                      <td>{log.resource_type}</td>
                      <td><code style={{ fontSize: 11 }}>{log.resource_id ? log.resource_id.slice(0, 8) + "..." : "-"}</code></td>
                      <td style={{ fontSize: 12 }}>{log.ip_address ?? "-"}</td>
                      <td><StatusPill value={log.response_status === 200 ? "OK" : String(log.response_status ?? "-")} /></td>
                    </motion.tr>
                  ))}
                </StaggerContainer>
                {auditLogs.length === 0 && <tr><td colSpan={6} className="empty">No audit logs found</td></tr>}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", gap: 8, padding: 12 }}>
                <motion.button className="icon-button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} whileTap={{ scale: 0.95 }}>Prev</motion.button>
                <span style={{ lineHeight: "36px", fontSize: 13, color: "#64746f" }}>Page {page} of {totalPages}</span>
                <motion.button className="icon-button" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} whileTap={{ scale: 0.95 }}>Next</motion.button>
              </div>
            )}
          </div>
        </FadeIn>
      )}

      {activeTab === "api" && (
        <FadeIn delay={0.2}>
          <div className="panel">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Method</th>
                  <th>Endpoint</th>
                  <th>Status</th>
                  <th>Response Time</th>
                  <th>IP Address</th>
                </tr>
              </thead>
              <tbody>
                <StaggerContainer stagger={0.03}>
                  {apiLogs.map((log) => (
                    <motion.tr key={log.id} variants={staggerItem}>
                      <td style={{ fontSize: 12, whiteSpace: "nowrap" }}>{log.created_at}</td>
                      <td><StatusPill value={log.method} /></td>
                      <td style={{ fontSize: 12, maxWidth: 250, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{log.endpoint}</td>
                      <td><StatusPill value={log.response_status === 200 ? "OK" : String(log.response_status)} /></td>
                      <td style={{ fontSize: 12 }}>{log.response_time_ms != null ? `${log.response_time_ms}ms` : "-"}</td>
                      <td style={{ fontSize: 12 }}>{log.ip_address ?? "-"}</td>
                    </motion.tr>
                  ))}
                </StaggerContainer>
                {apiLogs.length === 0 && <tr><td colSpan={6} className="empty">No API logs found</td></tr>}
              </tbody>
            </table>
          </div>
        </FadeIn>
      )}
    </section>
  );
}
