import { ReactNode } from "react";
import { motion, type Variants } from "framer-motion";

/* ─── Shared presets ─── */
export const ease = [0.25, 0.1, 0.25, 1] as const;

/* ─── FadeIn ─── */
type FadeInProps = {
  children: ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
};

export function FadeIn({ children, delay = 0, duration = 0.4, y = 12, className }: FadeInProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration, ease }}
    >
      {children}
    </motion.div>
  );
}

/* ─── ScaleIn ─── */
type ScaleInProps = {
  children: ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
};

export function ScaleIn({ children, delay = 0, duration = 0.35, className }: ScaleInProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration, ease }}
    >
      {children}
    </motion.div>
  );
}

/* ─── SlideUp ─── */
type SlideUpProps = {
  children: ReactNode;
  delay?: number;
  distance?: number;
  className?: string;
};

export function SlideUp({ children, delay = 0, distance = 40, className }: SlideUpProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: distance }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay, duration: 0.5, ease }}
    >
      {children}
    </motion.div>
  );
}

/* ─── StaggerContainer + StaggerItem ─── */
type StaggerContainerProps = {
  children: ReactNode;
  stagger?: number;
  className?: string;
};

const staggerVariants: Variants = {
  hidden: {},
  visible: (stagger: number) => ({
    transition: { staggerChildren: stagger },
  }),
};

export function StaggerContainer({ children, stagger = 0.06, className }: StaggerContainerProps) {
  return (
    <motion.div
      className={className}
      variants={staggerVariants}
      custom={stagger}
      initial="hidden"
      animate="visible"
    >
      {children}
    </motion.div>
  );
}

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease } },
};

/* ─── HoverCard — lifts on hover ─── */
type HoverCardProps = {
  children: ReactNode;
  className?: string;
};

export function HoverCard({ children, className }: HoverCardProps) {
  return (
    <motion.div
      className={className}
      whileHover={{ y: -3, boxShadow: "0 8px 24px rgba(0,0,0,0.08)" }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}

/* ─── AnimateOnPress ─── */
type PressProps = {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
};

export function AnimateOnPress({ children, className, onClick }: PressProps) {
  return (
    <motion.div
      className={className}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      style={{ cursor: "pointer" }}
    >
      {children}
    </motion.div>
  );
}
