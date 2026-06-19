import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Check, Menu, X } from "lucide-react";
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
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

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
            <Link to="/signin" className="btn btn-primary btn-sm">Sign in</Link>
          </motion.div>
          <button
            className="mobile-nav-toggle landing-mobile-toggle"
            onClick={() => setMobileNavOpen(!mobileNavOpen)}
            aria-label={mobileNavOpen ? "Close navigation" : "Open navigation"}
          >
            {mobileNavOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>

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
                <Link to="/pricing" onClick={() => setMobileNavOpen(false)}>Pricing</Link>
                <Link to="/contact" onClick={() => setMobileNavOpen(false)}>Contact</Link>
                <Link to="/signin" className="btn btn-primary btn-sm" onClick={() => setMobileNavOpen(false)}>Sign in</Link>
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

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
                {plan.highlighted && <span className="pricing-badge">Most popular</span>}
                <h3>{plan.name}</h3>
                <div className="pricing-price">
                  <strong>{plan.price}</strong>
                  {plan.period && <span>{plan.period}</span>}
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
                <Link
                  to={plan.name === "Enterprise" ? "/contact" : "/signup"}
                  className={`btn ${plan.highlighted ? "btn-primary" : "btn-outline"} btn-lg pricing-cta`}
                >
                  {plan.cta} <ArrowRight size={16} />
                </Link>
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
            <Link to="/contact" className="btn btn-primary btn-lg">
              Contact us <ArrowRight size={18} />
            </Link>
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
