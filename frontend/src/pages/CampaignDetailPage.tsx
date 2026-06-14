import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { MetricCard } from "../components/MetricCard";
import { api, unwrap } from "../lib/api";

type Campaign = {
  id: string;
  name: string;
  description?: string;
  campaign_type: string;
  start_date: string;
  end_date: string;
  target_segment?: string;
  budget?: number;
  actual_customers?: number;
  expected_customers?: number;
  is_active: boolean;
};

type CampaignTarget = {
  id: string;
  customer_id: string;
  target_date: string;
  status: string;
  response_date?: string;
  offer_accepted?: boolean;
};

type CampaignResult = {
  id: string;
  total_targets: number;
  responses: number;
  conversions: number;
  revenue_impact: number;
  cost: number;
  roi: number;
};

type CampaignDetail = Campaign & {
  targets: CampaignTarget[];
  results: CampaignResult[];
};

export function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);

  useEffect(() => {
    if (!id) return;
    void unwrap<CampaignDetail>(api.get(`/campaigns/${id}`))
      .then(setCampaign)
      .catch(() => setCampaign(null));
  }, [id]);

  if (!campaign) return <section className="page"><p className="empty">Loading campaign...</p></section>;

  const result = campaign.results?.[0];
  const responseRate = result && result.total_targets > 0 ? (result.responses / result.total_targets) * 100 : 0;
  const conversionRate = result && result.responses > 0 ? (result.conversions / result.responses) * 100 : 0;

  const statusCounts = { pending: 0, sent: 0, delivered: 0, responded: 0 };
  (campaign.targets || []).forEach((t) => {
    if (t.status in statusCounts) statusCounts[t.status as keyof typeof statusCounts]++;
  });

  return (
    <section className="page">
      <Link to="/campaigns" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#64746f", textDecoration: "none", marginBottom: 8 }}>
        <ArrowLeft size={16} /> Back to Campaigns
      </Link>

      <div className="page-title">
        <h1>{campaign.name}</h1>
        <StatusPill value={campaign.is_active ? "Active" : "Inactive"} />
      </div>

      {campaign.description && <p style={{ color: "#64746f", marginTop: -8 }}>{campaign.description}</p>}

      <div className="metric-grid compact-metrics">
        <MetricCard label="Type" value={campaign.campaign_type} />
        <MetricCard label="Budget" value={`$${Number(campaign.budget ?? 0).toLocaleString()}`} />
        <MetricCard label="Targets" value={String(result?.total_targets ?? campaign.actual_customers ?? 0)} />
        <MetricCard label="Response Rate" value={`${responseRate.toFixed(1)}%`} />
        <MetricCard label="Conversions" value={String(result?.conversions ?? 0)} />
        <MetricCard label="ROI" value={result ? `${result.roi.toFixed(1)}%` : "-"} />
      </div>

      <div className="two-column">
        <div className="panel">
          <div className="panel-header">
            <h2>Campaign Details</h2>
          </div>
          <div style={{ display: "grid", gap: 10, padding: "12px 0" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #e7eee9", padding: "6px 0" }}>
              <span style={{ color: "#64746f", fontSize: 13 }}>Start Date</span>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{campaign.start_date}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #e7eee9", padding: "6px 0" }}>
              <span style={{ color: "#64746f", fontSize: 13 }}>End Date</span>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{campaign.end_date}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #e7eee9", padding: "6px 0" }}>
              <span style={{ color: "#64746f", fontSize: 13 }}>Target Segment</span>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{campaign.target_segment ?? "-"}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #e7eee9", padding: "6px 0" }}>
              <span style={{ color: "#64746f", fontSize: 13 }}>Expected Customers</span>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{campaign.expected_customers ?? "-"}</span>
            </div>
          </div>

          {result && (
            <div style={{ padding: "12px 0", borderTop: "1px solid #dbe5df" }}>
              <h3 style={{ fontSize: 14, marginBottom: 10 }}>Financial Results</h3>
              <div style={{ display: "grid", gap: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
                  <span style={{ color: "#64746f", fontSize: 13 }}>Revenue Impact</span>
                  <span style={{ fontWeight: 700, fontSize: 13, color: "#146b45" }}>${Number(result.revenue_impact ?? 0).toLocaleString()}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
                  <span style={{ color: "#64746f", fontSize: 13 }}>Campaign Cost</span>
                  <span style={{ fontWeight: 700, fontSize: 13 }}>${Number(result.cost ?? 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>Target Pipeline</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, padding: "16px 0" }}>
            {(["pending", "sent", "delivered", "responded"] as const).map((status) => (
              <div key={status} style={{ textAlign: "center", padding: 12, background: "#f8faf9", borderRadius: 8, border: "1px solid #e7eee9" }}>
                <div style={{ fontSize: 24, fontWeight: 800, color: "#1d8a8a" }}>{statusCounts[status]}</div>
                <div style={{ fontSize: 12, color: "#64746f", textTransform: "capitalize" }}>{status}</div>
              </div>
            ))}
          </div>

          <div style={{ padding: "0 0 12px" }}>
            <h3 style={{ fontSize: 14, marginBottom: 10 }}>Target Customers</h3>
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Status</th>
                  <th>Offer Accepted</th>
                </tr>
              </thead>
              <tbody>
                {(campaign.targets || []).slice(0, 10).map((target) => (
                  <tr key={target.id}>
                    <td><code style={{ fontSize: 12 }}>{target.customer_id.slice(0, 8)}...</code></td>
                    <td><StatusPill value={target.status} /></td>
                    <td>{target.offer_accepted ? "Yes" : target.offer_accepted === false ? "No" : "-"}</td>
                  </tr>
                ))}
                {(!campaign.targets || campaign.targets.length === 0) && (
                  <tr><td colSpan={3} className="empty">No targets assigned</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
