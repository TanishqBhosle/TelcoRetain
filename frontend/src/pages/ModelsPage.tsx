import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
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
      <div className="page-title"><h1>Model Monitoring</h1></div>
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
            {models.map((model) => (
              <tr key={model.id}>
                <td><strong>{model.name}</strong><span>{model.training_date}</span></td>
                <td>{model.model_type}</td>
                <td>{model.version}</td>
                <td>{model.auc_score?.toFixed(3) ?? "-"}</td>
                <td>{model.accuracy?.toFixed(3) ?? "-"}</td>
                <td><StatusPill value={model.is_active ? "Active" : "Inactive"} /></td>
                <td><button className="icon-button" title="Retrain" onClick={() => void retrain(model.id)}><RefreshCw size={16} /></button></td>
              </tr>
            ))}
            {!models.length ? <tr><td colSpan={7} className="empty">No models registered</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
