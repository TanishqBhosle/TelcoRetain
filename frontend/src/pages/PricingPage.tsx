import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Check } from "lucide-react";
import { FadeIn, StaggerContainer, staggerItem, SlideUp } from "../components/animations";

const plans = [
  {
    name: "Starter",
    price: "$299",
    period: "/month",
    description: "For small operators getting started with retention analytics.",
    features: [
      "Up to 10,000 customers",
      "Single ML model",
      "Basic dashboard",
      "Churn predictions",
      "Email support",
    ],
    cta: "Start free trial",
    highlighted: false,
  },
  {
    name: "Professional",
    price: "$799",
    period: "/month",
    description: "For growing teams that need advanced analytics and campaigns.",
    features: [
      "Up to 100,000 customers",
      "Ensemble ML models",
      "Advanced dashboards",
      "SHAP explanations",
      "Campaign management",
      "Retention offers",
      "Priority support",
    ],
    cta: "Start free trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large operators with custom requirements.",
    features: [
      "Unlimited customers",
      "Custom ML models",
      "White-label option",
      "SSO / SAML",
      "Dedicated support",
      "SLA guarantee",
      "On-premise deployment",
    ],
    cta: "Contact sales",
    highlighted: false,
  },
];

export function PricingPage() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <motion.div className="brand" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }}>
            <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" />
          </motion.div>
          <motion.div className="landing-nav-links" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
            <Link to="/">Home</Link>
            <Link to="/about">About</Link>
            <Link to="/pricing" className="nav-active">Pricing</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/signin" className="primary-button" style={{ minHeight: 36, padding: "0 16px", fontSize: 13 }}>Sign in</Link>
          </motion.div>
        </div>
      </header>

      <section className="pricing-hero">
        <motion.div
          className="pricing-hero-inner"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <motion.span className="hero-badge" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>Pricing</motion.span>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>Simple, transparent pricing</motion.h1>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>Start free. Scale as you grow. No hidden fees.</motion.p>
        </motion.div>
      </section>

      <section className="pricing-cards">
        <StaggerContainer stagger={0.15}>
          <div className="pricing-grid">
            {plans.map((plan) => (
              <motion.div
                key={plan.name}
                className={`pricing-card ${plan.highlighted ? "pricing-highlighted" : ""}`}
                variants={staggerItem}
                whileHover={{ y: -6, boxShadow: "0 16px 40px rgba(0,0,0,0.1)" }}
              >
                {plan.highlighted ? <span className="pricing-badge">Most popular</span> : null}
                <h3>{plan.name}</h3>
                <div className="pricing-price">
                  <strong>{plan.price}</strong>
                  {plan.period ? <span>{plan.period}</span> : null}
                </div>
                <p className="pricing-desc">{plan.description}</p>
                <ul className="pricing-features">
                  {plan.features.map((f) => (
                    <li key={f}>
                      <Check size={16} />
                      {f}
                    </li>
                  ))}
                </ul>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Link
                    to={plan.name === "Enterprise" ? "/contact" : "/signup"}
                    className={`primary-button ${plan.highlighted ? "" : "pricing-outline"}`}
                    style={{ width: "100%", minHeight: 44, justifyContent: "center" }}
                  >
                    {plan.cta} <ArrowRight size={16} />
                  </Link>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </StaggerContainer>
      </section>

      <SlideUp>
        <section className="cta-section">
          <div className="cta-inner">
            <h2>Questions about pricing?</h2>
            <p>Our team can help you find the right plan for your operation.</p>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link to="/contact" className="primary-button" style={{ minHeight: 48, padding: "0 28px", fontSize: 15 }}>
                Contact us <ArrowRight size={18} />
              </Link>
            </motion.div>
          </div>
        </section>
      </SlideUp>

      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <div className="brand"><img src="/logo.svg" alt="TelcoRetain" className="brand-logo" /></div>
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
