import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FadeIn } from "../components/animations";
import { api, unwrap } from "../lib/api";

type Region = { region: string; customer_count: number; churn_count: number; revenue_at_risk: number };
type Operator = { operator: string; customer_count: number; churn_count: number; revenue_at_risk: number };

export function AnalyticsPage() {
  const [regions, setRegions] = useState<Region[]>([]);
  const [operators, setOperators] = useState<Operator[]>([]);

  useEffect(() => {
    void Promise.all([
      unwrap<{ regions: Region[] }>(api.get("/dashboard/regional-analysis")).then((data) => setRegions(data.regions)).catch(() => setRegions([])),
      unwrap<{ operators: Operator[] }>(api.get("/dashboard/operator-analysis")).then((data) => setOperators(data.operators)).catch(() => setOperators([]))
    ]);
  }, []);

  return (
    <section className="page split-panels">
      <FadeIn delay={0.1}>
        <motion.div
          className="panel tall"
          whileHover={{ boxShadow: "0 4px 20px rgba(0,0,0,0.06)" }}
          transition={{ duration: 0.2 }}
        >
          <div className="panel-header"><h1>Regional Risk</h1></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regions}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d9e2dc" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="churn_count" fill="#b84a62" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </FadeIn>

      <FadeIn delay={0.25}>
        <motion.div
          className="panel tall"
          whileHover={{ boxShadow: "0 4px 20px rgba(0,0,0,0.06)" }}
          transition={{ duration: 0.2 }}
        >
          <div className="panel-header"><h1>Operator Exposure</h1></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={operators}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d9e2dc" />
              <XAxis dataKey="operator" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="revenue_at_risk" fill="#1d8a8a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </FadeIn>
    </section>
  );
}
