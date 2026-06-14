import { motion } from "framer-motion";

type MetricCardProps = {
  label: string;
  value: string;
  delta?: string;
};

export function MetricCard({ label, value, delta }: MetricCardProps) {
  return (
    <motion.div
      className="metric-card"
      whileHover={{ y: -2, boxShadow: "0 6px 16px rgba(0,0,0,0.06)" }}
      transition={{ duration: 0.2 }}
    >
      <span>{label}</span>
      <strong>{value}</strong>
      {delta ? <small>{delta}</small> : null}
    </motion.div>
  );
}
