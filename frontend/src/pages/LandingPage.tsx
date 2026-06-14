import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Cable,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import { FadeIn, SlideUp, StaggerContainer, staggerItem } from "../components/animations";

const features = [
  {
    icon: BrainCircuit,
    title: "ML-Powered Predictions",
    description:
      "Ensemble models (XGBoost, LightGBM) predict churn risk with 83%+ AUC accuracy.",
  },
  {
    icon: Sparkles,
    title: "SHAP Explainability",
    description:
      "Every prediction comes with feature-level explanations so your team understands why.",
  },
  {
    icon: BarChart3,
    title: "Real-Time Analytics",
    description:
      "Dashboards for churn trends, revenue at risk, regional analysis, and operator exposure.",
  },
  {
    icon: Users,
    title: "Customer 360 View",
    description:
      "Unified profiles with usage, recharge history, support tickets, and timeline events.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description:
      "JWT auth, RBAC roles, rate limiting, audit logging, and account lockout protection.",
  },
  {
    icon: Cable,
    title: "Campaign Management",
    description:
      "Create retention campaigns, track targeting, and measure conversion outcomes.",
  },
];

const stats = [
  { value: "83%+", label: "Model AUC" },
  { value: "20+", label: "Database Tables" },
  { value: "40+", label: "API Endpoints" },
  { value: "<200ms", label: "Prediction Latency" },
];

export function LandingPage() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <motion.div
            className="brand"
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Cable size={22} />
            <span>Telco Retain</span>
          </motion.div>
          <motion.div
            className="landing-nav-links"
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <Link to="/about">About</Link>
            <Link to="/pricing">Pricing</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/signin" className="primary-button" style={{ minHeight: 36, padding: "0 16px", fontSize: 13 }}>
              Sign in
            </Link>
          </motion.div>
        </div>
      </header>

      <section className="hero">
        <motion.div
          className="hero-inner"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
        >
          <motion.span
            className="hero-badge"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            Telecom Customer Retention Intelligence
          </motion.span>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            Predict churn.<br />
            Retain customers.<br />
            Grow revenue.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            An AI-powered platform that identifies at-risk subscribers, explains
            why they might leave, and recommends the best retention offers — all
            in real time.
          </motion.p>
          <motion.div
            className="hero-actions"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link to="/signup" className="primary-button" style={{ minHeight: 48, padding: "0 24px", fontSize: 15 }}>
                Get started free <ArrowRight size={18} />
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link to="/about" className="secondary-button">
                Learn more
              </Link>
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      <SlideUp>
        <section className="stats-bar">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              className="stat-item"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.4 }}
            >
              <strong>{s.value}</strong>
              <span>{s.label}</span>
            </motion.div>
          ))}
        </section>
      </SlideUp>

      <section className="features-section">
        <SlideUp>
          <div className="features-header">
            <h2>Everything you need to reduce churn</h2>
            <p>From prediction to action — a complete retention intelligence stack.</p>
          </div>
        </SlideUp>
        <StaggerContainer stagger={0.1}>
          <div className="features-grid">
            {features.map((f) => (
              <motion.div
                key={f.title}
                className="feature-card"
                variants={staggerItem}
                whileHover={{ y: -6, boxShadow: "0 12px 32px rgba(0,0,0,0.1)" }}
                transition={{ duration: 0.25 }}
              >
                <div className="feature-icon">
                  <f.icon size={24} />
                </div>
                <h3>{f.title}</h3>
                <p>{f.description}</p>
              </motion.div>
            ))}
          </div>
        </StaggerContainer>
      </section>

      <SlideUp>
        <section className="cta-section">
          <div className="cta-inner">
            <h2>Ready to reduce churn?</h2>
            <p>Start predicting and preventing customer attrition today.</p>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link to="/signup" className="primary-button" style={{ minHeight: 48, padding: "0 28px", fontSize: 15 }}>
                Create your account <ArrowRight size={18} />
              </Link>
            </motion.div>
          </div>
        </section>
      </SlideUp>

      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <div className="brand">
            <Cable size={18} />
            <span>Telco Retain</span>
          </div>
          <div className="footer-links">
            <Link to="/about">About</Link>
            <Link to="/pricing">Pricing</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/signin">Sign in</Link>
          </div>
          <small>&copy; {new Date().getFullYear()} Telco Retain. All rights reserved.</small>
        </div>
      </footer>
    </div>
  );
}
