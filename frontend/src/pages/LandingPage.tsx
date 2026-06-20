import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  BrainCircuit,
  Target,
  Layers,
  BarChart3,
  Shield,
  Zap,
  Menu,
  X,
} from "lucide-react";

/* ─── Types ─── */
type Feature = { icon: typeof BrainCircuit; title: string; description: string };
type Stat = { value: string; label: string };

/* ─── Data ─── */
const stats: Stat[] = [
  { value: "150,000+", label: "Customers Analyzed" },
  { value: "98%", label: "Prediction Accuracy" },
  { value: "30%", label: "Churn Reduction" },
];

const features: Feature[] = [
  {
    icon: BrainCircuit,
    title: "ML Churn Prediction",
    description: "Predict at-risk customers with ensemble models and explainable AI insights.",
  },
  {
    icon: Target,
    title: "Explainable AI Insights",
    description: "Understand churn drivers with SHAP explanations and actionable reason codes.",
  },
  {
    icon: Layers,
    title: "Retention Recommendations",
    description: "Generate personalized offers — discounts, bonuses, and loyalty rewards.",
  },
  {
    icon: BarChart3,
    title: "Real-Time Analytics",
    description: "Monitor KPIs, trends, and campaign performance with live dashboards.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "GDPR compliant with role-based access, encryption, and audit logs.",
  },
  {
    icon: Zap,
    title: "Campaign Automation",
    description: "Launch targeted retention campaigns with smart audience segmentation.",
  },
];

/* ─── Animation Variants ─── */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.15 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as [number, number, number, number] } },
};

/* ─── Main Landing Page ─── */
export function LandingPage() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="landing">
      {/* Sticky Marketing Navigation */}
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <div className="brand">
            <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" />
          </div>
          <div className="landing-nav-links">
            <Link to="/" className="nav-active">Home</Link>
            <Link to="/about">About</Link>
            <Link to="/signin" className="btn btn-primary btn-sm">Sign in</Link>
          </div>
          <button
            className="mobile-nav-toggle landing-mobile-toggle"
            onClick={() => setMobileNavOpen(!mobileNavOpen)}
            aria-label={mobileNavOpen ? "Close navigation" : "Open navigation"}
          >
            {mobileNavOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>

      {/* Mobile Navigation Drawer */}
      <AnimatePresence>
        {mobileNavOpen && (
          <>
            <motion.div
              className="mobile-nav-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileNavOpen(false)}
            />
            <motion.aside
              className="mobile-nav-drawer"
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            >
              <div className="mobile-sidebar-brand">TelcoRetain</div>
              <nav className="mobile-drawer-links">
                <Link to="/" onClick={() => setMobileNavOpen(false)}>Home</Link>
                <Link to="/about" onClick={() => setMobileNavOpen(false)}>About</Link>
                <Link to="/signin" className="btn btn-primary btn-sm" onClick={() => setMobileNavOpen(false)}>Sign in</Link>
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-inner">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
          >
            Predict and Prevent Customer Churn
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.25, 0.1, 0.25, 1] }}
          >
            AI-powered retention platform helping telecom operators reduce churn, protect revenue, and build lasting customer loyalty.
          </motion.p>
          <motion.div
            className="hero-actions"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
          >
            <Link to="/signup" className="btn btn-primary btn-lg">
              Get Started <ArrowRight size={18} />
            </Link>
            <Link to="/about" className="secondary-button">
              Learn More <ArrowRight size={18} />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Social Proof Stats Bar */}
      <motion.div
        className="stats-bar"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-40px" }}
        variants={containerVariants}
      >
        {stats.map((stat) => (
          <motion.div key={stat.label} className="stat-item" variants={itemVariants}>
            <strong>{stat.value}</strong>
            <span>{stat.label}</span>
          </motion.div>
        ))}
      </motion.div>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-header">
          <h2>Built for Telecom Retention</h2>
          <p>Everything your team needs to predict, prevent, and manage customer churn.</p>
        </div>
        <motion.div
          className="features-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          variants={containerVariants}
        >
          {features.map((feature) => (
            <motion.div key={feature.title} className="feature-card" variants={itemVariants}>
              <div className="feature-icon">
                <feature.icon size={24} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Final CTA Section */}
      <section className="cta-section">
        <motion.div
          className="cta-inner"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2>Start Reducing Churn Today</h2>
          <p>
            Join leading telecom operators who trust TelcoRetain to protect revenue and grow customer loyalty.
          </p>
          <Link to="/signup" className="btn btn-primary btn-lg">
            Get Started Free <ArrowRight size={18} />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <span>&copy; {new Date().getFullYear()} TelcoRetain. All rights reserved.</span>
          <div className="footer-links">
            <Link to="/about">About</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

