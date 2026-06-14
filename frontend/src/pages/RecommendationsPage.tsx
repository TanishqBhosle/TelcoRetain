import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { FadeIn, StaggerContainer, staggerItem, HoverCard } from "../components/animations";
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
      <FadeIn>
        <div className="page-title">
          <h1>Retention Offers</h1>
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <form className="inline-form" onSubmit={submit}>
          <input value={customerId} onChange={(event) => setCustomerId(event.target.value)} placeholder="Customer UUID" />
          <motion.button className="primary-button" whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
            <Sparkles size={16} /> Generate
          </motion.button>
        </form>
      </FadeIn>

      <StaggerContainer stagger={0.08}>
        <div className="card-grid">
          {items.map((item) => (
            <HoverCard key={item.id}>
              <motion.article className="item-card" variants={staggerItem}>
                <div className="panel-header">
                  <h2>{item.offer_type.replace("_", " ")}</h2>
                  <StatusPill value={item.status} />
                </div>
                <p>{item.description}</p>
                <small>{item.validity_days} days - {item.expected_impact ?? "MEDIUM"} impact</small>
              </motion.article>
            </HoverCard>
          ))}
          {!items.length ? <p className="empty">No recommendations generated</p> : null}
        </div>
      </StaggerContainer>
    </section>
  );
}
