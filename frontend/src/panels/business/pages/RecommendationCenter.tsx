import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Check, X, Clock, DollarSign, Target } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type Recommendation = {
  id: string;
  customer_id: string;
  offer_type: string;
  description: string;
  validity_days: number;
  expected_impact: string;
  score: number;
  status: string;
  priority: string;
};

export function RecommendationCenter() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<Recommendation[]>(api.get("/recommendations/history"))
      .then(setRecommendations)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="business-page-header"
      >
        <div>
          <h2 className="business-page-title">Recommendation Center</h2>
          <p className="business-page-subtitle">AI-powered retention offers for at-risk customers</p>
        </div>
        <button className="business-btn primary">
          <Sparkles size={16} /> Generate Recommendations
        </button>
      </motion.div>

      <div className="business-recommendations-grid">
        {loading ? (
          <div className="business-loading">Loading recommendations...</div>
        ) : recommendations.length === 0 ? (
          <div className="business-empty">No recommendations yet. Generate recommendations for your customers.</div>
        ) : (
          recommendations.map((rec, i) => (
            <motion.div
              key={rec.id}
              className="business-recommendation-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="business-rec-header">
                <Sparkles size={20} />
                <span className={`business-rec-type ${rec.offer_type.toLowerCase()}`}>
                  {rec.offer_type}
                </span>
                <span className={`business-rec-priority ${rec.priority.toLowerCase()}`}>
                  {rec.priority}
                </span>
              </div>
              <div className="business-rec-content">
                <p>{rec.description}</p>
                <div className="business-rec-meta">
                  <span><Clock size={14} /> {rec.validity_days} days</span>
                  <span><Target size={14} /> {rec.expected_impact}</span>
                  <span><DollarSign size={14} /> Score: {(rec.score * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="business-rec-actions">
                <span className={`business-rec-status ${rec.status.toLowerCase()}`}>
                  {rec.status}
                </span>
                {rec.status === "pending" && (
                  <div className="business-rec-buttons">
                    <button className="business-icon-btn success"><Check size={16} /></button>
                    <button className="business-icon-btn danger"><X size={16} /></button>
                  </div>
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
