import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Target, Users, Zap, Menu, X } from "lucide-react";
import { FadeIn, SlideUp, StaggerContainer, staggerItem } from "../components/animations";

const team = [
  { role: "Platform Architecture", detail: "FastAPI + SQLAlchemy 2.0 async backend" },
  { role: "ML Engineering", detail: "XGBoost, LightGBM, SHAP explainability" },
  { role: "Frontend Development", detail: "React + TypeScript + Vite SPA" },
  { role: "Data Engineering", detail: "Neon PostgreSQL with 20+ normalized tables" },
];

export function AboutPage() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <motion.div className="brand" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }}>
            <img src="/logo.svg" alt="TelcoRetain" className="brand-logo" />
          </motion.div>
          <motion.div className="landing-nav-links" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
            <Link to="/" style={{ fontWeight: 700 }}>Home</Link>
            <Link to="/about" className="nav-active">About</Link>
            <Link to="/pricing">Pricing</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/signin" className="btn btn-primary btn-sm" style={{ fontSize: 13 }}>Sign in</Link>
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

      <section className="about-hero">
        <motion.div
          className="about-hero-inner"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <motion.span className="hero-badge" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>About Telco Retain</motion.span>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>Built for telecom retention teams</motion.h1>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
            Telco Retain is an intelligent customer retention platform designed
            specifically for telecom operators. It combines machine learning
            predictions with actionable insights to help you keep the customers
            that matter most.
          </motion.p>
        </motion.div>
      </section>

      <section className="about-mission">
        <div className="about-mission-inner">
          <FadeIn>
            <div className="about-mission-text">
              <h2>Our Mission</h2>
              <p>
                Customer churn costs telecom operators billions each year. We built
                Telco Retain to give retention teams the tools they need to
                understand <em>why</em> customers leave and <em>what</em> to do
                about it — before it's too late.
              </p>
              <p>
                Unlike generic analytics tools, Telco Retain is purpose-built for
                telecom: it understands ARPU, recharge cycles, network quality
                impacts, and plan change behaviors out of the box.
              </p>
            </div>
          </FadeIn>
          <StaggerContainer stagger={0.12}>
            <div className="about-mission-values">
              {[
                { icon: Target, title: "Precision", desc: "83%+ AUC models trained on real telecom datasets." },
                { icon: Zap, title: "Speed", desc: "Real-time predictions in under 200ms per customer." },
                { icon: Users, title: "Actionability", desc: "From insight to offer generation in a single workflow." },
              ].map((v) => (
                <motion.div
                  key={v.title}
                  className="value-card"
                  variants={staggerItem}
                  whileHover={{ y: -4, boxShadow: "var(--shadow-md)" }}
                  style={{
                    background: "var(--color-surface-raised)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-xl)",
                    padding: "var(--space-7)",
                  }}
                >
                  <v.icon size={28} style={{ color: "var(--color-primary)" }} />
                  <h3>{v.title}</h3>
                  <p>{v.desc}</p>
                </motion.div>
              ))}
            </div>
          </StaggerContainer>
        </div>
      </section>

      <section className="about-tech">
        <SlideUp>
          <div className="about-tech-inner">
            <h2>Built on modern infrastructure</h2>
            <p className="about-tech-subtitle">
              Every layer of the stack is designed for reliability, performance, and maintainability.
            </p>
            <StaggerContainer stagger={0.1}>
              <div className="tech-grid">
                {team.map((t) => (
                  <motion.div
                    key={t.role}
                    className="tech-card"
                    variants={staggerItem}
                    whileHover={{ y: -3 }}
                    style={{
                      background: "var(--color-surface)",
                      border: "1px solid var(--color-border)",
                      borderRadius: "var(--radius-xl)",
                      padding: "var(--space-6)",
                    }}
                  >
                    <h3>{t.role}</h3>
                    <p>{t.detail}</p>
                  </motion.div>
                ))}
              </div>
            </StaggerContainer>
          </div>
        </SlideUp>
      </section>

      <SlideUp>
        <section className="cta-section">
          <div className="cta-inner">
            <h2>See it in action</h2>
            <p>Get started with Telco Retain today.</p>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Link to="/signup" className="btn btn-primary btn-lg">
                Create your account <ArrowRight size={18} />
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
