import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Database, Upload, Plus, Eye, Trash2, Search } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type Dataset = {
  id: string;
  name: string;
  description: string;
  dataset_type: string;
  format: string;
  row_count: number;
  column_count: number;
  is_active: boolean;
  created_at: string;
};

export function DatasetManagement() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    unwrap<Dataset[]>(api.get("/datasets"))
      .then(setDatasets)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filteredDatasets = datasets.filter(
    (d) => d.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="admin-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="admin-page-header"
      >
        <div>
          <h2 className="admin-page-title">Dataset Management</h2>
          <p className="admin-page-subtitle">Upload and manage training datasets</p>
        </div>
        <button className="admin-btn primary">
          <Upload size={16} /> Upload Dataset
        </button>
      </motion.div>

      <div className="admin-search-bar">
        <Search size={18} />
        <input
          type="text"
          placeholder="Search datasets..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="admin-datasets-grid">
        {loading ? (
          <div className="admin-loading">Loading datasets...</div>
        ) : filteredDatasets.length === 0 ? (
          <div className="admin-empty">No datasets found</div>
        ) : (
          filteredDatasets.map((dataset, i) => (
            <motion.div
              key={dataset.id}
              className="admin-dataset-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="admin-dataset-icon">
                <Database size={24} />
              </div>
              <div className="admin-dataset-info">
                <h3>{dataset.name}</h3>
                <p>{dataset.description || "No description"}</p>
                <div className="admin-dataset-meta">
                  <span className="admin-tag">{dataset.format.toUpperCase()}</span>
                  <span className="admin-tag">{dataset.dataset_type}</span>
                  <span className="admin-tag">{dataset.row_count.toLocaleString()} rows</span>
                  <span className="admin-tag">{dataset.column_count} cols</span>
                </div>
              </div>
              <div className="admin-dataset-actions">
                <button className="admin-icon-btn" title="View Versions">
                  <Eye size={16} />
                </button>
                <button className="admin-icon-btn danger" title="Delete">
                  <Trash2 size={16} />
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
