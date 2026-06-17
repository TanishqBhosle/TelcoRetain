import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, AlertTriangle, CheckCircle, TrendingUp, Search, Users } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type Customer = {
  id: string;
  customer_id: string;
  full_name: string;
  operator: string;
  region: string;
};

type PredictionResult = {
  id: string;
  customer_id: string;
  churn_probability: number;
  risk_score: number;
  risk_category: string;
  confidence_score: number;
  features_used: Record<string, any>;
};

export function ChurnPrediction() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<string>("");
  const [search, setSearch] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    unwrap<{ items: Customer[] }>(api.get("/customers?limit=50"))
      .then((data) => setCustomers(data.items || []))
      .catch(() => {})
      .finally(() => setLoadingCustomers(false));
  }, []);

  const filteredCustomers = customers.filter(
    (c) =>
      c.full_name.toLowerCase().includes(search.toLowerCase()) ||
      c.customer_id.toLowerCase().includes(search.toLowerCase())
  );

  const handlePredict = async () => {
    if (!selectedCustomer) {
      setError("Please select a customer");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await unwrap<PredictionResult>(
        api.post("/predictions/predict", { customer_id: selectedCustomer })
      );
      setResult(response);
    } catch (err: any) {
      const msg = err?.response?.data?.message || err.message || "Prediction failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const selectedName = customers.find((c) => c.id === selectedCustomer)?.full_name;

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="business-page-title">Churn Prediction</h2>
        <p className="business-page-subtitle">Predict customer churn risk using ensemble ML models</p>
      </motion.div>

      <motion.div
        className="business-prediction-form"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.4 }}
      >
        <h3><Users size={20} /> Select Customer</h3>
        <div className="business-search-bar" style={{ marginBottom: 12 }}>
          <Search size={18} />
          <input
            type="text"
            placeholder="Search customers by name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="business-customer-select">
          {loadingCustomers ? (
            <div className="business-loading">Loading customers...</div>
          ) : (
            <div className="business-customer-list">
              {filteredCustomers.slice(0, 10).map((customer) => (
                <div
                  key={customer.id}
                  className={`business-customer-option ${selectedCustomer === customer.id ? "selected" : ""}`}
                  onClick={() => setSelectedCustomer(customer.id)}
                >
                  <div className="business-avatar">{customer.full_name.charAt(0)}</div>
                  <div>
                    <span className="business-customer-name">{customer.full_name}</span>
                    <span className="business-customer-id">{customer.customer_id} · {customer.operator} · {customer.region}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="business-form-row" style={{ marginTop: 16 }}>
          <span style={{ fontSize: 14, color: "#64748b" }}>
            {selectedName ? `Selected: ${selectedName}` : "No customer selected"}
          </span>
          <button className="business-btn primary" onClick={handlePredict} disabled={loading || !selectedCustomer}>
            <BrainCircuit size={16} />
            {loading ? "Predicting..." : "Run Prediction"}
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
                  style={{
                    width: `${result.churn_probability * 100}%`,
                    background: result.risk_category === "HIGH" ? "#ef4444" : result.risk_category === "MEDIUM" ? "#f59e0b" : "#10b981",
                  }}
                />
              </div>
            </div>

            <div className="business-result-card">
              <div className="business-result-label">Risk Score</div>
              <div className="business-result-value">
                {result.risk_score} / 100
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
            <a href="/app/explain" className="business-btn secondary">View SHAP Explanation</a>
            <a href="/app/recommendations" className="business-btn primary">Generate Retention Offers</a>
          </div>
        </motion.div>
      )}
    </div>
  );
}
