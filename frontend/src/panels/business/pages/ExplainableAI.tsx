import { motion } from "framer-motion";
import { Lightbulb, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from "lucide-react";

export function ExplainableAI() {
  const features = [
    { name: "tenure_months", value: 12, shap_value: -0.15, importance: 1 },
    { name: "monthly_charges", value: 89.99, shap_value: 0.12, importance: 2 },
    { name: "contract_type", value: "Month-to-month", shap_value: 0.10, importance: 3 },
    { name: "total_charges", value: 1079.88, shap_value: -0.08, importance: 4 },
    { name: "payment_method", value: "Electronic check", shap_value: 0.06, importance: 5 },
  ];

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Explainable AI</h2>
        <p className="business-page-subtitle">Understand why predictions are made with SHAP explanations</p>
      </motion.div>

      <motion.div
        className="business-explain-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.4 }}
      >
        <h3>
          <Lightbulb size={20} /> Feature Importance
        </h3>
        <p className="business-explain-description">
          SHAP values show how each feature contributes to the churn prediction.
          Positive values push towards churn, negative values push towards retention.
        </p>

        <div className="business-features-list">
          {features.map((feature, i) => (
            <motion.div
              key={feature.name}
              className="business-feature-item"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.05, duration: 0.3 }}
            >
              <div className="business-feature-header">
                <span className="business-feature-rank">#{feature.importance}</span>
                <span className="business-feature-name">{feature.name}</span>
                <span className="business-feature-value">{feature.value}</span>
              </div>
              <div className="business-feature-bar-container">
                <div className="business-feature-bar-label">
                  <TrendingDown size={12} /> Retention
                </div>
                <div className="business-feature-bar">
                  <div
                    className={`business-feature-bar-fill ${feature.shap_value > 0 ? "positive" : "negative"}`}
                    style={{
                      width: `${Math.abs(feature.shap_value) * 500}%`,
                      marginLeft: feature.shap_value < 0 ? `${50 - Math.abs(feature.shap_value) * 500}%` : "50%",
                    }}
                  />
                  <div className="business-feature-bar-center" />
                </div>
                <div className="business-feature-bar-label">
                  Churn <TrendingUp size={12} />
                </div>
              </div>
              <div className="business-feature-shap">
                SHAP Value: <span className={feature.shap_value > 0 ? "text-danger" : "text-success"}>
                  {feature.shap_value > 0 ? "+" : ""}{feature.shap_value.toFixed(3)}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      <motion.div
        className="business-explain-summary"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <h3>Summary</h3>
        <div className="business-summary-content">
          <div className="business-summary-item">
            <AlertTriangle size={16} className="text-danger" />
            <span>Short tenure (12 months) increases churn risk</span>
          </div>
          <div className="business-summary-item">
            <AlertTriangle size={16} className="text-danger" />
            <span>High monthly charges ($89.99) contribute to churn</span>
          </div>
          <div className="business-summary-item">
            <AlertTriangle size={16} className="text-danger" />
            <span>Month-to-month contract type is a risk factor</span>
          </div>
          <div className="business-summary-item">
            <CheckCircle size={16} className="text-success" />
            <span>Higher total charges indicate customer loyalty</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
