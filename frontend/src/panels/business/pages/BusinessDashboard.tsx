import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, TrendingDown, DollarSign, AlertTriangle, Target, BarChart3, Activity } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type DashboardKPI = {
  total_customers: number;
  churn_rate: number;
  revenue_at_risk: number;
  high_risk_customers: number;
  active_campaigns: number;
  arpu: number;
};

export function BusinessDashboard() {
  const [kpis, setKpis] = useState<DashboardKPI | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<DashboardKPI>(api.get("/dashboard/kpis"))
      .then(setKpis)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const kpiCards = [
    {
      label: "Total Customers",
      value: kpis?.total_customers?.toLocaleString() ?? "0",
      icon: Users,
      color: "#6366f1",
      trend: "+2.5%",
    },
    {
      label: "Churn Rate",
      value: `${kpis?.churn_rate?.toFixed(1) ?? 0}%`,
      icon: TrendingDown,
      color: "#ef4444",
      trend: "-1.2%",
    },
    {
      label: "Revenue at Risk",
      value: `$${(kpis?.revenue_at_risk ?? 0).toLocaleString()}`,
      icon: DollarSign,
      color: "#f59e0b",
      trend: "+5.3%",
    },
    {
      label: "High Risk Customers",
      value: kpis?.high_risk_customers?.toLocaleString() ?? "0",
      icon: AlertTriangle,
      color: "#f97316",
      trend: "-3.1%",
    },
    {
      label: "Active Campaigns",
      value: kpis?.active_campaigns?.toString() ?? "0",
      icon: Target,
      color: "#10b981",
      trend: "+2",
    },
    {
      label: "ARPU",
      value: `$${kpis?.arpu?.toFixed(2) ?? "0"}`,
      icon: BarChart3,
      color: "#8b5cf6",
      trend: "+$2.50",
    },
  ];

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
              <span className="business-kpi-value">{loading ? "..." : kpi.value}</span>
              <span className={`business-kpi-trend ${kpi.trend.startsWith("+") ? "positive" : "negative"}`}>
                {kpi.trend}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

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
