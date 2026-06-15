import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Plus, Play, CheckCircle, AlertCircle, Clock } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type MLModel = {
  id: string;
  name: string;
  version: string;
  model_type: string;
  accuracy: number;
  auc_score: number;
  is_active: boolean;
  training_date: string;
  description: string;
};

export function ModelRegistry() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<MLModel[]>(api.get("/models"))
      .then(setModels)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="admin-page-header"
      >
        <div>
          <h2 className="admin-page-title">Model Registry</h2>
          <p className="admin-page-subtitle">Manage ML models and their versions</p>
        </div>
        <button className="admin-btn primary">
          <Plus size={16} /> Register Model
        </button>
      </motion.div>

      <div className="admin-models-grid">
        {loading ? (
          <div className="admin-loading">Loading models...</div>
        ) : models.length === 0 ? (
          <div className="admin-empty">No models registered</div>
        ) : (
          models.map((model, i) => (
            <motion.div
              key={model.id}
              className={`admin-model-card ${model.is_active ? "active" : ""}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="admin-model-header">
                <BrainCircuit size={24} />
                <div>
                  <h3>{model.name}</h3>
                  <span className="admin-version">v{model.version}</span>
                </div>
                {model.is_active && (
                  <span className="admin-active-badge">
                    <CheckCircle size={14} /> Active
                  </span>
                )}
              </div>
              <div className="admin-model-stats">
                <div className="admin-stat">
                  <span className="admin-stat-label">Accuracy</span>
                  <span className="admin-stat-value">{(model.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="admin-stat">
                  <span className="admin-stat-label">AUC Score</span>
                  <span className="admin-stat-value">{model.auc_score?.toFixed(3) ?? "N/A"}</span>
                </div>
              </div>
              <div className="admin-model-meta">
                <span className="admin-tag">{model.model_type}</span>
                <span className="admin-tag">
                  <Clock size={12} /> {new Date(model.training_date).toLocaleDateString()}
                </span>
              </div>
              <div className="admin-model-actions">
                <button className="admin-btn secondary">
                  <Play size={14} /> Retrain
                </button>
                {!model.is_active && (
                  <button className="admin-btn primary">Activate</button>
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
