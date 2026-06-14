import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { BrainCircuit } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { api, unwrap } from "../lib/api";

type Prediction = {
  id: string;
  customer_id: string;
  churn_probability: number;
  risk_score: number;
  risk_category: string;
  confidence_score?: number;
};

export function PredictionPage() {
  const [customerId, setCustomerId] = useState("");
  const [bulkIds, setBulkIds] = useState("");
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [bulkResult, setBulkResult] = useState<{ success_count: number; failure_count: number; total_processed: number } | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"single" | "bulk">("single");

  async function submitSingle(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPrediction(null);
    try {
      const result = await unwrap<Prediction>(api.post("/predictions/predict", { customer_id: customerId }));
      setPrediction(result);
    } catch {
      setError("Prediction could not be completed.");
    }
  }

  async function submitBulk(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBulkResult(null);
    const ids = bulkIds.split("\n").map((s) => s.trim()).filter(Boolean);
    if (!ids.length) {
      setError("Enter at least one customer ID.");
      return;
    }
    try {
      const result = await unwrap<{ success_count: number; failure_count: number; total_processed: number }>(
        api.post("/predictions/bulk", { customer_ids: ids })
      );
      setBulkResult(result);
    } catch {
      setError("Bulk prediction failed.");
    }
  }

  return (
    <section className="page">
      <div className="page-title">
        <h1>Churn Prediction</h1>
        <BrainCircuit size={22} />
      </div>

      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid #dbe5df", marginBottom: 0 }}>
        {(["single", "bulk"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "10px 16px",
              border: "none",
              background: activeTab === tab ? "#1d8a8a" : "transparent",
              color: activeTab === tab ? "#fff" : "#64746f",
              fontWeight: 700,
              fontSize: 13,
              cursor: "pointer",
              borderRadius: "8px 8px 0 0",
            }}
          >
            {tab === "single" ? "Single Prediction" : "Bulk Prediction"}
          </button>
        ))}
      </div>

      {activeTab === "single" && (
        <div className="two-column">
          <div className="panel">
            <div className="panel-header"><h2>Customer Prediction</h2></div>
            <form className="form compact" onSubmit={submitSingle}>
              <label>
                Customer UUID
                <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="00000000-0000-0000-0000-000000000000" />
              </label>
              <button className="primary-button">Run prediction</button>
            </form>
            {error && <p className="error-text">{error}</p>}
          </div>
          <div className="panel">
            <div className="panel-header">
              <h2>Result</h2>
              {prediction && <StatusPill value={prediction.risk_category} />}
            </div>
            {prediction ? (
              <div className="result-grid">
                <span>Risk score</span><strong>{prediction.risk_score}</strong>
                <span>Probability</span><strong>{Math.round(prediction.churn_probability * 100)}%</strong>
                <span>Confidence</span><strong>{Math.round((prediction.confidence_score ?? 0) * 100)}%</strong>
                <span>Prediction ID</span>
                <Link to={`/predict/${prediction.id}`} style={{ color: "#1d8a8a", fontWeight: 600, fontSize: 13 }}>
                  View Details
                </Link>
              </div>
            ) : (
              <p className="empty">No prediction selected</p>
            )}
          </div>
        </div>
      )}

      {activeTab === "bulk" && (
        <div className="panel" style={{ maxWidth: 600 }}>
          <div className="panel-header"><h2>Bulk Prediction</h2></div>
          <form className="form compact" onSubmit={submitBulk}>
            <label>
              Customer UUIDs (one per line)
              <textarea
                value={bulkIds}
                onChange={(e) => setBulkIds(e.target.value)}
                rows={6}
                style={{ width: "100%", padding: 10, border: "1px solid #cddbd3", borderRadius: 8, fontSize: 13, fontFamily: "monospace", resize: "vertical" }}
                placeholder={"00000000-0000-0000-0000-000000000001\n00000000-0000-0000-0000-000000000002"}
              />
            </label>
            <button className="primary-button">Run bulk prediction</button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {bulkResult && (
            <div className="result-grid" style={{ marginTop: 14 }}>
              <span>Total processed</span><strong>{bulkResult.total_processed}</strong>
              <span>Successful</span><strong style={{ color: "#146b45" }}>{bulkResult.success_count}</strong>
              <span>Failed</span><strong style={{ color: "#9d2340" }}>{bulkResult.failure_count}</strong>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
