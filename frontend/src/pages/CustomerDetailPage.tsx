import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Phone, MapPin, Calendar, CreditCard } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { MetricCard } from "../components/MetricCard";
import { api, unwrap } from "../lib/api";

type Customer = {
  id: string;
  customer_id: string;
  full_name: string;
  email: string;
  phone_number: string;
  gender?: string;
  age?: number;
  region?: string;
  operator?: string;
  join_date?: string;
  contract_type?: string;
  monthly_charges?: number;
  total_charges?: number;
  tenure_months?: number;
  arpu?: number;
  churn_status: boolean;
  status: string;
};

type TimelineEvent = {
  event_date: string;
  event_type: string;
  title: string;
  details: string;
  status: string;
};

type UsageMetric = {
  id: string;
  month: string;
  voice_minutes: number;
  data_gb: number;
  sms_count: number;
  arpu: number;
};

type Complaint = {
  id: string;
  ticket_date: string;
  ticket_type: string;
  complaint_type: string;
  description: string;
  resolution_status: string;
};

type Recharge = {
  id: string;
  recharge_date: string;
  amount: number;
  payment_method: string;
};

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [usage, setUsage] = useState<UsageMetric[]>([]);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [recharges, setRecharges] = useState<Recharge[]>([]);
  const [activeTab, setActiveTab] = useState<"timeline" | "usage" | "complaints" | "recharges">("timeline");

  useEffect(() => {
    if (!id) return;
    void Promise.all([
      unwrap<Customer>(api.get(`/customers/${id}`)).then(setCustomer).catch(() => setCustomer(null)),
      unwrap<TimelineEvent[]>(api.get(`/customers/${id}/timeline`)).then(setTimeline).catch(() => setTimeline([])),
      unwrap<UsageMetric[]>(api.get(`/customers/${id}/usage`)).then(setUsage).catch(() => setUsage([])),
      unwrap<Complaint[]>(api.get(`/customers/${id}/complaints`)).then(setComplaints).catch(() => setComplaints([])),
      unwrap<Recharge[]>(api.get(`/customers/${id}/recharge-history`)).then(setRecharges).catch(() => setRecharges([])),
    ]);
  }, [id]);

  if (!customer) return <section className="page"><p className="empty">Loading customer...</p></section>;

  const tabs = [
    { key: "timeline" as const, label: "Timeline" },
    { key: "usage" as const, label: "Usage" },
    { key: "complaints" as const, label: "Complaints" },
    { key: "recharges" as const, label: "Recharges" },
  ];

  return (
    <section className="page">
      <Link to="/customers" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#64746f", textDecoration: "none", marginBottom: 8 }}>
        <ArrowLeft size={16} /> Back to Customers
      </Link>

      <div className="page-title">
        <h1>{customer.full_name}</h1>
        <StatusPill value={customer.churn_status ? "Churned" : customer.status} />
      </div>

      <div className="metric-grid compact-metrics">
        <MetricCard label="ARPU" value={`$${Number(customer.arpu ?? 0).toLocaleString()}`} />
        <MetricCard label="Monthly Charges" value={`$${Number(customer.monthly_charges ?? 0).toLocaleString()}`} />
        <MetricCard label="Tenure" value={`${customer.tenure_months ?? 0} months`} />
        <MetricCard label="Total Charges" value={`$${Number(customer.total_charges ?? 0).toLocaleString()}`} />
      </div>

      <div className="panel">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12, padding: "16px 0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Phone size={16} color="#64746f" /><span>{customer.phone_number}</span></div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><MapPin size={16} color="#64746f" /><span>{customer.region ?? "-"}</span></div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Calendar size={16} color="#64746f" /><span>{customer.join_date ?? "-"}</span></div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><CreditCard size={16} color="#64746f" /><span>{customer.contract_type ?? "-"}</span></div>
        </div>
      </div>

      <div className="panel">
        <div style={{ display: "flex", gap: 4, borderBottom: "1px solid #dbe5df", marginBottom: 0 }}>
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: "10px 16px",
                border: "none",
                background: activeTab === tab.key ? "#1d8a8a" : "transparent",
                color: activeTab === tab.key ? "#fff" : "#64746f",
                fontWeight: 700,
                fontSize: 13,
                cursor: "pointer",
                borderRadius: "8px 8px 0 0",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ padding: "16px 0" }}>
          {activeTab === "timeline" && (
            <div style={{ display: "grid", gap: 12 }}>
              {timeline.length === 0 && <p className="empty">No timeline events</p>}
              {timeline.map((event, i) => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 12, padding: "10px 0", borderBottom: "1px solid #e7eee9" }}>
                  <span style={{ fontSize: 12, color: "#64746f" }}>{event.event_date}</span>
                  <div>
                    <strong style={{ fontSize: 14 }}>{event.title}</strong>
                    <p style={{ margin: 0, fontSize: 13, color: "#64746f" }}>{event.details}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "usage" && (
            <table>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Voice (min)</th>
                  <th>Data (GB)</th>
                  <th>SMS</th>
                  <th>ARPU</th>
                </tr>
              </thead>
              <tbody>
                {usage.map((u) => (
                  <tr key={u.id}>
                    <td>{u.month}</td>
                    <td>{u.voice_minutes}</td>
                    <td>{u.data_gb?.toFixed(1)}</td>
                    <td>{u.sms_count}</td>
                    <td>${u.arpu?.toFixed(2)}</td>
                  </tr>
                ))}
                {usage.length === 0 && <tr><td colSpan={5} className="empty">No usage data</td></tr>}
              </tbody>
            </table>
          )}

          {activeTab === "complaints" && (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Complaint</th>
                  <th>Description</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((c) => (
                  <tr key={c.id}>
                    <td>{c.ticket_date}</td>
                    <td>{c.ticket_type}</td>
                    <td>{c.complaint_type}</td>
                    <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.description}</td>
                    <td><StatusPill value={c.resolution_status ?? "Open"} /></td>
                  </tr>
                ))}
                {complaints.length === 0 && <tr><td colSpan={5} className="empty">No complaints</td></tr>}
              </tbody>
            </table>
          )}

          {activeTab === "recharges" && (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Payment Method</th>
                </tr>
              </thead>
              <tbody>
                {recharges.map((r) => (
                  <tr key={r.id}>
                    <td>{r.recharge_date}</td>
                    <td>${r.amount?.toFixed(2)}</td>
                    <td>{r.payment_method}</td>
                  </tr>
                ))}
                {recharges.length === 0 && <tr><td colSpan={3} className="empty">No recharge history</td></tr>}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </section>
  );
}
