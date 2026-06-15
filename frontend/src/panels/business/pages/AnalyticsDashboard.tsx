import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, Users, DollarSign, Target } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type AnalyticsData = {
  churn_trends: { month: string; churn_rate: number }[];
  regional_analysis: { region: string; customer_count: number; churn_rate: number }[];
  operator_analysis: { operator: string; customer_count: number; churn_rate: number; arpu: number }[];
};

export function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      unwrap<any>(api.get("/dashboard/churn-trends")),
      unwrap<any>(api.get("/dashboard/regional-analysis")),
      unwrap<any>(api.get("/dashboard/operator-analysis")),
    ])
      .then(([churnTrends, regional, operator]) => {
        setData({
          churn_trends: churnTrends?.data || [],
          regional_analysis: regional?.data || [],
          operator_analysis: operator?.data || [],
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Analytics Dashboard</h2>
        <p className="business-page-subtitle">Comprehensive analytics and insights</p>
      </motion.div>

      <div className="business-analytics-grid">
        <motion.div
          className="business-analytics-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <h3><TrendingDown size={20} /> Churn Trends</h3>
          {loading ? (
            <div className="business-loading">Loading...</div>
          ) : (
            <div className="business-chart-placeholder">
              <p>Churn trends chart would be displayed here</p>
              <div className="business-chart-bars">
                {data?.churn_trends?.slice(0, 6).map((trend, i) => (
                  <div key={i} className="business-chart-bar-item">
                    <div
                      className="business-chart-bar"
                      style={{ height: `${trend.churn_rate * 10}px` }}
                    />
                    <span>{trend.month}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          className="business-analytics-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <h3><Users size={20} /> Regional Analysis</h3>
          {loading ? (
            <div className="business-loading">Loading...</div>
          ) : (
            <div className="business-chart-placeholder">
              <p>Regional analysis would be displayed here</p>
              <div className="business-chart-bars">
                {data?.regional_analysis?.slice(0, 6).map((region, i) => (
                  <div key={i} className="business-chart-bar-item">
                    <div
                      className="business-chart-bar"
                      style={{ height: `${region.customer_count / 100}px` }}
                    />
                    <span>{region.region}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          className="business-analytics-card full-width"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <h3><BarChart3 size={20} /> Operator Analysis</h3>
          {loading ? (
            <div className="business-loading">Loading...</div>
          ) : (
            <div className="business-table-container">
              <table className="business-table">
                <thead>
                  <tr>
                    <th>Operator</th>
                    <th>Customers</th>
                    <th>Churn Rate</th>
                    <th>ARPU</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.operator_analysis?.map((op, i) => (
                    <tr key={i}>
                      <td>{op.operator}</td>
                      <td>{op.customer_count.toLocaleString()}</td>
                      <td>
                        <span className={op.churn_rate > 20 ? "text-danger" : "text-success"}>
                          {op.churn_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td>${op.arpu.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
