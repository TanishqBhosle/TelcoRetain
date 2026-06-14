import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MetricCard } from "../components/MetricCard";
import { api, unwrap } from "../lib/api";

type Kpis = {
  total_customers: number;
  active_customers: number;
  average_churn_probability: number;
  revenue_at_risk: number;
  active_campaigns_count: number;
  campaign_conversion_rate: number;
};

type Trend = { period: string; average_churn_probability: number; predicted_churn_count: number };

export function DashboardPage() {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);

  useEffect(() => {
    void Promise.all([
      unwrap<Kpis>(api.get("/dashboard/kpis")).then(setKpis).catch(() => setKpis(null)),
      unwrap<{ trends: Trend[] }>(api.get("/dashboard/churn-trends")).then((data) => setTrends(data.trends)).catch(() => setTrends([]))
    ]);
  }, []);

  return (
    <section className="page">
      <div className="page-title">
        <h1>Retention Dashboard</h1>
      </div>
      <div className="metric-grid">
        <MetricCard label="Customers" value={String(kpis?.total_customers ?? 0)} />
        <MetricCard label="Active" value={String(kpis?.active_customers ?? 0)} />
        <MetricCard label="Average Risk" value={`${Math.round((kpis?.average_churn_probability ?? 0) * 100)}%`} />
        <MetricCard label="Revenue At Risk" value={`$${Number(kpis?.revenue_at_risk ?? 0).toLocaleString()}`} />
        <MetricCard label="Campaigns" value={String(kpis?.active_campaigns_count ?? 0)} />
        <MetricCard label="Conversion" value={`${Math.round((kpis?.campaign_conversion_rate ?? 0) * 100)}%`} />
      </div>
      <div className="panel tall">
        <div className="panel-header">
          <h2>Churn Trend</h2>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={trends}>
            <defs>
              <linearGradient id="risk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1d8a8a" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#1d8a8a" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#d9e2dc" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="average_churn_probability" stroke="#1d8a8a" fill="url(#risk)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
