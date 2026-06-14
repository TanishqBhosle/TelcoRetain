import { FormEvent, useState } from "react";
import { Sparkles } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { api, unwrap } from "../lib/api";

type Recommendation = {
  id: string;
  offer_type: string;
  description: string;
  validity_days: number;
  expected_impact?: string;
  score?: number;
  status: string;
};

export function RecommendationsPage() {
  const [customerId, setCustomerId] = useState("");
  const [items, setItems] = useState<Recommendation[]>([]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const data = await unwrap<Recommendation[]>(api.post("/recommendations/generate", { customer_id: customerId })).catch(() => []);
    setItems(data);
  }

  return (
    <section className="page">
      <div className="page-title">
        <h1>Retention Offers</h1>
      </div>
      <form className="inline-form" onSubmit={submit}>
        <input value={customerId} onChange={(event) => setCustomerId(event.target.value)} placeholder="Customer UUID" />
        <button className="primary-button"><Sparkles size={16} /> Generate</button>
      </form>
      <div className="card-grid">
        {items.map((item) => (
          <article className="item-card" key={item.id}>
            <div className="panel-header">
              <h2>{item.offer_type.replace("_", " ")}</h2>
              <StatusPill value={item.status} />
            </div>
            <p>{item.description}</p>
            <small>{item.validity_days} days - {item.expected_impact ?? "MEDIUM"} impact</small>
          </article>
        ))}
        {!items.length ? <p className="empty">No recommendations generated</p> : null}
      </div>
    </section>
  );
}
