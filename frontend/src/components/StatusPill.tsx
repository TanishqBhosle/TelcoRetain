import { motion } from "framer-motion";

export function StatusPill({ value }: { value: string }) {
  return (
    <motion.span
      className={`status status-${value.toLowerCase().replace(/\s+/g, "-")}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.25 }}
    >
      {value}
    </motion.span>
  );
}
