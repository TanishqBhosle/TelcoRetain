import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Megaphone, Plus, Eye, Edit, Calendar, Users, DollarSign, TrendingUp } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type Campaign = {
  id: string;
  name: string;
  description: string;
  campaign_type: string;
  start_date: string;
  end_date: string;
  target_segment: string;
  budget: number;
  expected_customers: number;
  actual_customers: number;
  is_active: boolean;
};

export function CampaignManagement() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap<Campaign[]>(api.get("/campaigns"))
      .then(setCampaigns)
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
          <h2 className="business-page-title">Campaign Management</h2>
          <p className="business-page-subtitle">Create and manage retention campaigns</p>
        </div>
        <button className="business-btn primary">
          <Plus size={16} /> Create Campaign
        </button>
      </motion.div>

      <div className="business-campaigns-grid">
        {loading ? (
          <div className="business-loading">Loading campaigns...</div>
        ) : campaigns.length === 0 ? (
          <div className="business-empty">No campaigns yet. Create your first campaign.</div>
        ) : (
          campaigns.map((campaign, i) => (
            <motion.div
              key={campaign.id}
              className={`business-campaign-card ${campaign.is_active ? "active" : ""}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
            >
              <div className="business-campaign-header">
                <Megaphone size={24} />
                <div>
                  <h3>{campaign.name}</h3>
                  <span className="business-campaign-type">{campaign.campaign_type}</span>
                </div>
                {campaign.is_active && <span className="business-active-badge">Active</span>}
              </div>
              <div className="business-campaign-content">
                <p>{campaign.description}</p>
                <div className="business-campaign-stats">
                  <div className="business-stat">
                    <Calendar size={14} />
                    <span>{new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}</span>
                  </div>
                  <div className="business-stat">
                    <Users size={14} />
                    <span>{campaign.actual_customers || 0} / {campaign.expected_customers} customers</span>
                  </div>
                  <div className="business-stat">
                    <DollarSign size={14} />
                    <span>Budget: ${campaign.budget.toLocaleString()}</span>
                  </div>
                </div>
              </div>
              <div className="business-campaign-actions">
                <button className="business-btn secondary">
                  <Eye size={14} /> View
                </button>
                <button className="business-btn secondary">
                  <Edit size={14} /> Edit
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
