import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingDown, Users, Globe } from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { api, unwrap } from "../../../lib/api";

type ChurnTrend = {
  period: string;
  average_churn_probability: number;
  predicted_churn_count: number;
};

type RegionalPoint = {
  region: string;
  customer_count: number;
  churn_count: number;
  average_churn_probability: number;
  revenue_at_risk: string;
};

type OperatorPoint = {
  operator: string;
  customer_count: number;
  churn_count: number;
  average_churn_probability: number;
  revenue_at_risk: string;
};

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#ec4899", "#14b8a6", "#84cc16"];

export function AnalyticsDashboard() {
  const [trends, setTrends] = useState<ChurnTrend[]>([]);
  const [regions, setRegions] = useState<RegionalPoint[]>([]);
  const [operators, setOperators] = useState<OperatorPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      unwrap<{ trends: ChurnTrend[] }>(api.get("/dashboard/churn-trends")),
      unwrap<{ regions: RegionalPoint[] }>(api.get("/dashboard/regional-analysis")),
      unwrap<{ operators: OperatorPoint[] }>(api.get("/dashboard/operator-analysis")),
    ])
      .then(([churnData, regionalData, operatorData]) => {
        setTrends(churnData?.trends || []);
        setRegions(regionalData?.regions || []);
        setOperators(operatorData?.operators || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const trendChartData = trends.map((t) => ({
    period: t.period,
    churnRate: +(t.average_churn_probability * 100).toFixed(1),
    churnCount: t.predicted_churn_count,
  }));

  const regionChartData = regions.slice(0, 8).map((r) => ({
    name: r.region,
    customers: r.customer_count,
    churnRate: +(r.average_churn_probability * 100).toFixed(1),
    revenue: +Number(r.revenue_at_risk).toFixed(0),
  }));

  const operatorChartData = operators.map((o) => ({
    name: o.operator,
    customers: o.customer_count,
    churnRate: +(o.average_churn_probability * 100).toFixed(1),
    revenue: +Number(o.revenue_at_risk).toFixed(0),
  }));

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Analytics Dashboard</h2>
        <p className="business-page-subtitle">Comprehensive churn analytics and regional insights</p>
      </motion.div>

      {loading ? (
        <div className="business-loading">Loading analytics...</div>
      ) : (
        <div className="business-analytics-grid">
          <motion.div
            className="business-analytics-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.4 }}
          >
            <h3><TrendingDown size={20} /> Churn Probability Trend</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trendChartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7eee9" />
                <XAxis dataKey="period" tick={{ fill: "#64746f", fontSize: 12 }} />
                <YAxis tick={{ fill: "#64746f", fontSize: 12 }} unit="%" />
                <Tooltip
                  contentStyle={{ background: "#fff", border: "1px solid #dbe5df", borderRadius: 8 }}
                  formatter={(value: number) => [`${value}%`, "Churn Rate"]}
                />
                <Line type="monotone" dataKey="churnRate" stroke="#ef4444" strokeWidth={3} dot={{ r: 5, fill: "#ef4444" }} />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div
            className="business-analytics-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            <h3><Globe size={20} /> Regional Customer Distribution</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={regionChartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7eee9" />
                <XAxis dataKey="name" tick={{ fill: "#64746f", fontSize: 11 }} angle={-20} textAnchor="end" height={50} />
                <YAxis tick={{ fill: "#64746f", fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: "#fff", border: "1px solid #dbe5df", borderRadius: 8 }}
                />
                <Bar dataKey="customers" radius={[4, 4, 0, 0]}>
                  {regionChartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div
            className="business-analytics-card full-width"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
          >
            <h3><BarChart3 size={20} /> Operator Analysis</h3>
            <div className="business-table-container" style={{ border: "none" }}>
              <table className="business-table">
                <thead>
                  <tr>
                    <th>Operator</th>
                    <th>Customers</th>
                    <th>Churn Count</th>
                    <th>Avg Churn Probability</th>
                    <th>Revenue at Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {operatorChartData.map((op, i) => (
                    <tr key={i}>
                      <td><strong>{op.name}</strong></td>
                      <td>{op.customers.toLocaleString()}</td>
                      <td>{operators[i]?.churn_count ?? 0}</td>
                      <td>
                        <span className={`business-status ${op.churnRate > 40 ? "high" : op.churnRate > 25 ? "medium" : "low"}`}>
                          {op.churnRate}%
                        </span>
                      </td>
                      <td>₹{op.revenue.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
