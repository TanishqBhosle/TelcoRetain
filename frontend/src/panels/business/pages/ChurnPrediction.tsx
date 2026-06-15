import { useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Play, AlertTriangle, CheckCircle, TrendingUp, TrendingDown } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type PredictionResult = {
  customer_id: string;
  churn_probability: number;
  risk_score: number;
  risk_category: string;
  confidence_score: number;
};

export function ChurnPrediction() {
  const [customerId, setCustomerId] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePredict = async () => {
    if (!customerId.trim()) {
      setError("Please enter a customer ID");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await unwrap<PredictionResult>(
        api.post("/predictions/predict", { customer_id: customerId })
      );
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Churn Prediction</h2>
        <p className="business-page-subtitle">Predict customer churn risk using ML models</p>
      </motion.div>

      <motion.div
        className="business-prediction-form"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.4 }}
      >
        <h3>Run Prediction</h3>
        <div className="business-form-row">
          <input
            type="text"
            placeholder="Enter Customer ID"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
          />
          <button className="business-btn primary" onClick={handlePredict} disabled={loading}>
            <BrainCircuit size={16} />
            {loading ? "Predicting..." : "Predict"}
          </button>
        </div>
        {error && <div className="business-error">{error}</div>}
      </motion.div>

      {result && (
        <motion.div
          className="business-prediction-result"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <h3>Prediction Results</h3>
          <div className="business-result-grid">
            <div className="business-result-card">
              <div className="business-result-icon">
                {result.risk_category === "HIGH" ? (
                  <AlertTriangle size={32} className="text-danger" />
                ) : result.risk_category === "MEDIUM" ? (
                  <TrendingUp size={32} className="text-warning" />
                ) : (
                  <CheckCircle size={32} className="text-success" />
                )}
              </div>
              <div className="business-result-label">Risk Category</div>
              <div className={`business-result-value ${result.risk_category.toLowerCase()}`}>
                {result.risk_category}
              </div>
            </div>

            <div className="business-result-card">
              <div className="business-result-label">Churn Probability</div>
              <div className="business-result-value">
                {(result.churn_probability * 100).toFixed(1)}%
              </div>
              <div className="business-progress-bar">
                <div
                  className="business-progress-fill"
                  style={{ width: `${result.churn_probability * 100}%` }}
                />
              </div>
            </div>

            <div className="business-result-card">
              <div className="business-result-label">Risk Score</div>
              <div className="business-result-value">
                {result.risk_score.toFixed(2)}
              </div>
            </div>

            <div className="business-result-card">
              <div className="business-result-label">Confidence</div>
              <div className="business-result-value">
                {(result.confidence_score * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="business-result-actions">
            <button className="business-btn secondary">View Explanation</button>
            <button className="business-btn primary">Generate Recommendations</button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
