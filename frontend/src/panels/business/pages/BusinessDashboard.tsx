import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, TrendingDown, TrendingUp, DollarSign, AlertTriangle, Target, BarChart3, Activity } from "lucide-react";
import { api, unwrap } from "../../../lib/api";
import { SkeletonLoader } from "../../../components/SkeletonLoader";
import { ErrorState } from "../../../components/ErrorState";

type DashboardKPI = {
  total_customers: number;
  active_customers: number;
  average_churn_probability: number;
  revenue_at_risk: string;
  active_campaigns_count: number;
  campaign_conversion_rate: number;
};

function getTrendClass(trend: string): "positive" | "negative" | "neutral" {
  if (trend.startsWith("+") && trend !== "+0" && trend !== "+0%") return "positive";
  if (trend.startsWith("-") && trend !== "-0" && trend !== "-0%") return "negative";
  return "neutral";
}

export function BusinessDashboard() {
  const [kpis, setKpis] = useState<DashboardKPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKpis = useCallback(() => {
    setLoading(true);
    setError(null);
    unwrap<DashboardKPI>(api.get("/dashboard/kpis"))
      .then(setKpis)
      .catch((err) => {
        setError(err?.message || "Failed to load dashboard data");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchKpis();
  }, [fetchKpis]);

  const churnPct = kpis ? (kpis.average_churn_probability * 100).toFixed(1) : "0";
  const highRisk = kpis ? Math.round(kpis.total_customers * kpis.average_churn_probability) : 0;

  const kpiCards = [
    {
      label: "Total Customers",
      value: kpis?.total_customers?.toLocaleString() ?? "0",
      icon: Users,
      color: "#6366f1",
      trend: "+2.5%",
    },
    {
      label: "Active Customers",
      value: kpis?.active_customers?.toLocaleString() ?? "0",
      icon: Activity,
      color: "#10b981",
      trend: "+4.1%",
    },
    {
      label: "Churn Probability",
      value: `${churnPct}%`,
      icon: TrendingDown,
      color: "#ef4444",
      trend: "-1.2%",
    },
    {
      label: "Revenue at Risk",
      value: `₹${Number(kpis?.revenue_at_risk ?? 0).toLocaleString()}`,
      icon: DollarSign,
      color: "#f59e0b",
      trend: "-5.3%",
    },
    {
      label: "High Risk Customers",
      value: highRisk.toLocaleString(),
      icon: AlertTriangle,
      color: "#f97316",
      trend: "-3.1%",
    },
    {
      label: "Active Campaigns",
      value: kpis?.active_campaigns_count?.toString() ?? "0",
      icon: Target,
      color: "#8b5cf6",
      trend: "+2",
    },
  ];

  if (error) {
    return (
      <div className="business-page">
        <ErrorState
          heading="Failed to load dashboard"
          description={error}
          onRetry={fetchKpis}
        />
      </div>
    );
  }

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Business Dashboard</h2>
        <p className="business-page-subtitle">Overview of key business metrics and retention insights</p>
      </motion.div>

      {loading ? (
        <SkeletonLoader variant="card" count={6} />
      ) : (
        <div className="business-kpi-grid">
          {kpiCards.map((kpi, i) => (
            <motion.div
              key={kpi.label}
              className="business-kpi-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="business-kpi-icon" style={{ backgroundColor: `${kpi.color}20`, color: kpi.color }}>
                <kpi.icon size={24} />
              </div>
              <div className="business-kpi-content">
                <span className="business-kpi-label">{kpi.label}</span>
                <span className="business-kpi-value">{kpi.value}</span>
                <span className={`business-kpi-trend ${getTrendClass(kpi.trend)}`}>
                  {getTrendClass(kpi.trend) === "positive" && <TrendingUp size={14} />}
                  {getTrendClass(kpi.trend) === "negative" && <TrendingDown size={14} />}
                  {kpi.trend}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <div className="business-section">
        <h3 className="business-section-title">Quick Actions</h3>
        <div className="business-actions-grid">
          <a href="/app/customers" className="business-action-card">
            <Users size={24} />
            <span>Customer Explorer</span>
          </a>
          <a href="/app/predict" className="business-action-card">
            <Activity size={24} />
            <span>Run Predictions</span>
          </a>
          <a href="/app/campaigns" className="business-action-card">
            <Target size={24} />
            <span>Manage Campaigns</span>
          </a>
          <a href="/app/analytics" className="business-action-card">
            <BarChart3 size={24} />
            <span>View Analytics</span>
          </a>
        </div>
      </div>
    </div>
  );
}
