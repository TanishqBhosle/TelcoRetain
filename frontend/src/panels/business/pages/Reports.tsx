import { motion } from "framer-motion";
import { FileBarChart, Download, Calendar, Filter } from "lucide-react";

export function Reports() {
  const reports = [
    { name: "Churn Risk Report", description: "Customers at high risk of churning", lastGenerated: "2024-01-15", status: "ready" },
    { name: "Campaign Performance", description: "Analysis of all active campaigns", lastGenerated: "2024-01-14", status: "ready" },
    { name: "Revenue Analysis", description: "Revenue trends and forecasting", lastGenerated: "2024-01-13", status: "ready" },
    { name: "Customer Segmentation", description: "Customer groups by behavior", lastGenerated: "2024-01-12", status: "ready" },
    { name: "Operator Comparison", description: "Performance across operators", lastGenerated: "2024-01-11", status: "ready" },
  ];

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="business-page-header"
      >
        <div>
          <h2 className="business-page-title">Reports</h2>
          <p className="business-page-subtitle">Generate and download business reports</p>
        </div>
      </motion.div>

      <div className="business-reports-grid">
        {reports.map((report, i) => (
          <motion.div
            key={report.name}
            className="business-report-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
          >
            <div className="business-report-icon">
              <FileBarChart size={24} />
            </div>
            <div className="business-report-info">
              <h3>{report.name}</h3>
              <p>{report.description}</p>
              <div className="business-report-meta">
                <span><Calendar size={14} /> Last generated: {report.lastGenerated}</span>
                <span className={`business-report-status ${report.status}`}>
                  {report.status === "ready" ? "Ready" : "Generating..."}
                </span>
              </div>
            </div>
            <div className="business-report-actions">
              <button className="business-btn secondary">
                <Download size={14} /> Download
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="business-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <h3 className="business-section-title">Schedule Reports</h3>
        <div className="business-schedule-form">
          <div className="business-form-row">
            <select>
              <option>Select Report</option>
              {reports.map((r) => (
                <option key={r.name}>{r.name}</option>
              ))}
            </select>
            <select>
              <option>Daily</option>
              <option>Weekly</option>
              <option>Monthly</option>
            </select>
            <button className="business-btn primary">Schedule</button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
