import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Megaphone, Plus } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { api, unwrap } from "../lib/api";

type Campaign = {
  id: string;
  name: string;
  campaign_type: string;
  start_date: string;
  end_date: string;
  target_segment?: string;
  budget?: number;
  actual_customers?: number;
  is_active: boolean;
};

export function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [name, setName] = useState("");

  function load() {
    void unwrap<Campaign[]>(api.get("/campaigns")).then(setCampaigns).catch(() => setCampaigns([]));
  }

  useEffect(load, []);

  async function createCampaign(event: FormEvent) {
    event.preventDefault();
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(today.getMonth() + 1);
    await api.post("/campaigns", {
      name,
      campaign_type: "retention",
      start_date: today.toISOString().slice(0, 10),
      end_date: nextMonth.toISOString().slice(0, 10),
      target_segment: "high_risk",
      is_active: true
    }).catch(() => null);
    setName("");
    load();
  }

  return (
    <section className="page">
      <div className="page-title">
        <h1>Campaigns</h1>
        <Megaphone size={24} />
      </div>
      <form className="inline-form" onSubmit={createCampaign}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Campaign name" />
        <button className="primary-button"><Plus size={16} /> Create</button>
      </form>
      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Window</th>
              <th>Segment</th>
              <th>Targets</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map((campaign) => (
              <tr key={campaign.id}>
                <td>
                  <Link to={`/campaigns/${campaign.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                    <strong style={{ color: "#1d8a8a" }}>{campaign.name}</strong>
                  </Link>
                </td>
                <td>{campaign.campaign_type}</td>
                <td>{campaign.start_date} to {campaign.end_date}</td>
                <td>{campaign.target_segment ?? "-"}</td>
                <td>{campaign.actual_customers ?? 0}</td>
                <td><StatusPill value={campaign.is_active ? "Active" : "Inactive"} /></td>
              </tr>
            ))}
            {!campaigns.length ? <tr><td colSpan={6} className="empty">No campaigns found</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
