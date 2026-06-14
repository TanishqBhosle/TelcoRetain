import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Cable, Mail, MapPin, Phone, Send } from "lucide-react";
import { FadeIn, SlideUp, StaggerContainer, staggerItem, ScaleIn } from "../components/animations";

export function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1000));
    setSubmitted(true);
    setLoading(false);
  }

  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <motion.div className="brand" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }}>
            <Cable size={22} />
            <span>Telco Retain</span>
          </motion.div>
          <motion.div className="landing-nav-links" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
            <Link to="/">Home</Link>
            <Link to="/about">About</Link>
            <Link to="/pricing">Pricing</Link>
            <Link to="/contact" className="nav-active">Contact</Link>
            <Link to="/signin" className="primary-button" style={{ minHeight: 36, padding: "0 16px", fontSize: 13 }}>Sign in</Link>
          </motion.div>
        </div>
      </header>

      <section className="contact-hero">
        <motion.div
          className="contact-hero-inner"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <motion.span className="hero-badge" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>Contact Us</motion.span>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>Get in touch</motion.h1>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>Have questions or need a demo? We'd love to hear from you.</motion.p>
        </motion.div>
      </section>

      <section className="contact-section">
        <div className="contact-grid">
          <FadeIn delay={0.2}>
            <div className="contact-info">
              <h2>Contact information</h2>
              <p>Reach out through any of the channels below, or fill out the form and we'll get back to you within 24 hours.</p>
              <StaggerContainer stagger={0.12}>
                <div className="contact-details">
                  {[
                    { icon: Mail, label: "Email", value: "support@telco-retain.com" },
                    { icon: Phone, label: "Phone", value: "+1 (555) 123-4567" },
                    { icon: MapPin, label: "Office", value: "123 Innovation Drive, San Francisco, CA 94105" },
                  ].map((d) => (
                    <motion.div key={d.label} className="contact-detail" variants={staggerItem} whileHover={{ x: 4 }}>
                      <d.icon size={20} />
                      <div>
                        <strong>{d.label}</strong>
                        <span>{d.value}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </StaggerContainer>
            </div>
          </FadeIn>

          <FadeIn delay={0.35}>
            <div className="contact-form-panel">
              {submitted ? (
                <ScaleIn>
                  <div className="contact-success">
                    <Send size={40} />
                    <h3>Message sent!</h3>
                    <p>Thank you for reaching out. We'll get back to you within 24 hours.</p>
                    <Link to="/" className="primary-button" style={{ minWidth: 140, justifyContent: "center" }}>
                      Back to home
                    </Link>
                  </div>
                </ScaleIn>
              ) : (
                <form onSubmit={submit} className="form">
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
                    Name
                    <input value={name} onChange={(e) => setName(e.target.value)} type="text" required placeholder="Your full name" />
                  </motion.label>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 }}>
                    Email
                    <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder="you@company.com" />
                  </motion.label>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}>
                    Subject
                    <input value={subject} onChange={(e) => setSubject(e.target.value)} type="text" required placeholder="How can we help?" />
                  </motion.label>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.55 }}>
                    Message
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      rows={5}
                      required
                      placeholder="Tell us about your requirements..."
                      style={{ resize: "vertical", minHeight: 100, padding: "10px 12px" }}
                    />
                  </motion.label>
                  <motion.button
                    className="primary-button"
                    disabled={loading}
                    style={{ width: "100%", justifyContent: "center" }}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {loading ? "Sending..." : "Send message"}
                  </motion.button>
                </form>
              )}
            </div>
          </FadeIn>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <div className="brand"><Cable size={18} /><span>Telco Retain</span></div>
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
