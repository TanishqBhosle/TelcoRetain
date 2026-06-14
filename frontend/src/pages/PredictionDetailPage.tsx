import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, BrainCircuit } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { FadeIn, StaggerContainer, staggerItem, ScaleIn } from "../components/animations";
import { api, unwrap } from "../lib/api";

type Prediction = {
  id: string;
  customer_id: string;
  model_id: string;
  prediction_date: string;
  churn_probability: number;
  risk_score: number;
  risk_category: string;
  confidence_score?: number;
  features_used?: Record<string, number>;
};

type FeatureExplanation = {
  feature_name: string;
  shap_value: number;
  feature_value: number;
  feature_importance_rank: number;
};

type Explanation = {
  prediction_id: string;
  model_id: string;
  explanation_date: string;
  features: FeatureExplanation[];
  top_drivers: string[];
  reasons: string[];
};

export function PredictionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);

  useEffect(() => {
    if (!id) return;
    void Promise.all([
      unwrap<Prediction>(api.get(`/predictions/${id}`)).then(setPrediction).catch(() => setPrediction(null)),
      unwrap<Explanation>(api.get(`/predictions/${id}/explanation`)).then(setExplanation).catch(() => setExplanation(null)),
    ]);
  }, [id]);

  if (!prediction) return <section className="page"><p className="empty">Loading prediction...</p></section>;

  const maxShap = explanation
    ? Math.max(...explanation.features.map((f) => Math.abs(f.shap_value)), 1)
    : 1;

  return (
    <section className="page">
      <FadeIn>
        <Link to="/predict" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#64746f", textDecoration: "none", marginBottom: 8 }}>
          <ArrowLeft size={16} /> Back to Predictions
        </Link>

        <div className="page-title">
          <h1>Prediction Detail</h1>
          <StatusPill value={prediction.risk_category} />
        </div>
      </FadeIn>

      <StaggerContainer stagger={0.08}>
        <motion.div className="metric-grid compact-metrics" variants={staggerItem}>
          <div className="metric-card">
            <span>Churn Probability</span>
            <strong>{Math.round(prediction.churn_probability * 100)}%</strong>
          </div>
          <div className="metric-card">
            <span>Risk Score</span>
            <strong>{prediction.risk_score}</strong>
          </div>
          <div className="metric-card">
            <span>Confidence</span>
            <strong>{Math.round((prediction.confidence_score ?? 0) * 100)}%</strong>
          </div>
          <div className="metric-card">
            <span>Prediction Date</span>
            <strong style={{ fontSize: 14 }}>{prediction.prediction_date}</strong>
          </div>
        </motion.div>
      </StaggerContainer>

      <div className="two-column">
        <FadeIn delay={0.3}>
          <div className="panel">
            <div className="panel-header">
              <h2><BrainCircuit size={18} style={{ verticalAlign: "middle", marginRight: 6 }} /> SHAP Feature Impact</h2>
            </div>
            {explanation && explanation.features.length > 0 ? (
              <div style={{ padding: "12px 0" }}>
                <StaggerContainer stagger={0.04}>
                  {explanation.features
                    .sort((a, b) => a.feature_importance_rank - b.feature_importance_rank)
                    .map((feature) => {
                      const isPositive = feature.shap_value > 0;
                      const barWidth = Math.abs(feature.shap_value) / maxShap * 100;
                      return (
                        <motion.div
                          key={feature.feature_name}
                          variants={staggerItem}
                          style={{ display: "grid", gridTemplateColumns: "140px 1fr 80px", gap: 10, alignItems: "center", padding: "8px 0", borderBottom: "1px solid #e7eee9" }}
                        >
                          <span style={{ fontSize: 13, fontWeight: 600 }}>{feature.feature_name.replace(/_/g, " ")}</span>
                          <div style={{ position: "relative", height: 18, background: "#e7eee9", borderRadius: 4 }}>
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${barWidth / 2}%` }}
                              transition={{ delay: 0.5, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
                              style={{
                                position: "absolute",
                                top: 0,
                                left: isPositive ? "50%" : `${50 - barWidth / 2}%`,
                                height: "100%",
                                background: isPositive ? "#b84a62" : "#146b45",
                                borderRadius: 4,
                              }}
                            />
                            <div style={{ position: "absolute", left: "50%", top: 0, width: 1, height: "100%", background: "#999" }} />
                          </div>
                          <span style={{ fontSize: 12, color: isPositive ? "#b84a62" : "#146b45", fontWeight: 700, textAlign: "right" }}>
                            {isPositive ? "+" : ""}{feature.shap_value.toFixed(3)}
                          </span>
                        </motion.div>
                      );
                    })}
                </StaggerContainer>
              </div>
            ) : (
              <p className="empty">No explanation available yet</p>
            )}
          </div>
        </FadeIn>

        <FadeIn delay={0.4}>
          <div className="panel">
            <div className="panel-header">
              <h2>Churn Reasons</h2>
            </div>
            {explanation && explanation.reasons.length > 0 ? (
              <div style={{ padding: "12px 0", display: "grid", gap: 10 }}>
                <StaggerContainer stagger={0.06}>
                  {explanation.reasons.map((reason, i) => (
                    <motion.div
                      key={i}
                      variants={staggerItem}
                      whileHover={{ x: 4, backgroundColor: "#f0f5f1" }}
                      style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 12px", background: "#f8faf9", borderRadius: 8, border: "1px solid #e7eee9" }}
                    >
                      <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 24, height: 24, borderRadius: 12, background: "#1d8a8a", color: "#fff", fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                        {i + 1}
                      </span>
                      <span style={{ fontSize: 14 }}>{reason}</span>
                    </motion.div>
                  ))}
                </StaggerContainer>
              </div>
            ) : (
              <p className="empty">No reasons generated</p>
            )}

            {prediction.features_used && (
              <div style={{ marginTop: 16, padding: "12px 0", borderTop: "1px solid #dbe5df" }}>
                <h3 style={{ fontSize: 14, marginBottom: 10 }}>Raw Features Used</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                  {Object.entries(prediction.features_used).map(([key, value]) => (
                    <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid #e7eee9" }}>
                      <span style={{ fontSize: 12, color: "#64746f" }}>{key.replace(/_/g, " ")}</span>
                      <span style={{ fontSize: 12, fontWeight: 700 }}>{typeof value === "number" ? value.toFixed(2) : String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
