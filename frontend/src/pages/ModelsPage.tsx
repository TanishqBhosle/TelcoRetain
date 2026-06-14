import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { RefreshCw } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { FadeIn, StaggerContainer, staggerItem } from "../components/animations";
import { api, unwrap } from "../lib/api";

type Model = {
  id: string;
  name: string;
  version: string;
  model_type: string;
  training_date: string;
  accuracy?: number;
  auc_score?: number;
  is_active: boolean;
};

export function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);

  function load() {
    void unwrap<Model[]>(api.get("/models")).then(setModels).catch(() => setModels([]));
  }

  useEffect(load, []);

  async function retrain(id: string) {
    await api.put(`/models/${id}/retrain`, {}).catch(() => null);
  }

  return (
    <section className="page">
      <FadeIn>
        <div className="page-title"><h1>Model Monitoring</h1></div>
      </FadeIn>

      <FadeIn delay={0.15}>
        <div className="table-panel">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Type</th>
                <th>Version</th>
                <th>AUC</th>
                <th>Accuracy</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <StaggerContainer stagger={0.05}>
                {models.map((model) => (
                  <motion.tr key={model.id} variants={staggerItem}>
                    <td><strong>{model.name}</strong><span>{model.training_date}</span></td>
                    <td>{model.model_type}</td>
                    <td>{model.version}</td>
                    <td>{model.auc_score?.toFixed(3) ?? "-"}</td>
                    <td>{model.accuracy?.toFixed(3) ?? "-"}</td>
                    <td><StatusPill value={model.is_active ? "Active" : "Inactive"} /></td>
                    <td>
                      <motion.button
                        className="icon-button"
                        title="Retrain"
                        onClick={() => void retrain(model.id)}
                        whileHover={{ scale: 1.1, rotate: 90 }}
                        whileTap={{ scale: 0.9 }}
                        transition={{ duration: 0.2 }}
                      >
                        <RefreshCw size={16} />
                      </motion.button>
                    </td>
                  </motion.tr>
                ))}
              </StaggerContainer>
              {!models.length ? <tr><td colSpan={7} className="empty">No models registered</td></tr> : null}
            </tbody>
          </table>
        </div>
      </FadeIn>
    </section>
  );
}
