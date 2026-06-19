import { FormEvent, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, Mail, MapPin, Phone, Send, Menu, X } from "lucide-react";
import { FadeIn, StaggerContainer, staggerItem, ScaleIn } from "../components/animations";

interface FormErrors {
  name?: string;
  email?: string;
  message?: string;
}

function validateName(value: string): string | undefined {
  if (!value.trim()) return "Name is required.";
  if (value.trim().length > 100) return "Name must be 100 characters or fewer.";
  return undefined;
}

function validateEmail(value: string): string | undefined {
  if (!value.trim()) return "Email is required.";
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value.trim())) return "Please enter a valid email address.";
  return undefined;
}

function validateMessage(value: string): string | undefined {
  if (!value.trim()) return "Message is required.";
  if (value.trim().length > 2000) return "Message must be 2000 characters or fewer.";
  return undefined;
}

function validateAll(name: string, email: string, message: string): FormErrors {
  const errors: FormErrors = {};
  const nameErr = validateName(name);
  const emailErr = validateEmail(email);
  const msgErr = validateMessage(message);
  if (nameErr) errors.name = nameErr;
  if (emailErr) errors.email = emailErr;
  if (msgErr) errors.message = msgErr;
  return errors;
}

export function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const handleBlur = useCallback((field: "name" | "email" | "message") => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => {
      const newErrors = { ...prev };
      if (field === "name") {
        const err = validateName(name);
        if (err) newErrors.name = err;
        else delete newErrors.name;
      } else if (field === "email") {
        const err = validateEmail(email);
        if (err) newErrors.email = err;
        else delete newErrors.email;
      } else if (field === "message") {
        const err = validateMessage(message);
        if (err) newErrors.message = err;
        else delete newErrors.message;
      }
      return newErrors;
    });
  }, [name, email, message]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitError(null);

    // Mark all fields as touched
    setTouched({ name: true, email: true, message: true });

    // Validate all fields
    const validationErrors = validateAll(name, email, message);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setLoading(true);
    try {
      // Simulate network request
      await new Promise<void>((resolve, reject) => {
        setTimeout(() => {
          // Simulate success (in production this would be an actual API call)
          resolve();
        }, 1000);
      });
      setSubmitted(true);
    } catch {
      setSubmitError("Unable to send your message. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  }

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
            <Link to="/pricing">Pricing</Link>
            <Link to="/contact" className="nav-active">Contact</Link>
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
                    <CheckCircle size={48} />
                    <h3>Message sent!</h3>
                    <p>Thank you for reaching out. We'll get back to you within 24 hours.</p>
                    <Link to="/" className="btn btn-primary" style={{ minWidth: 140, justifyContent: "center" }}>
                      Back to home
                    </Link>
                  </div>
                </ScaleIn>
              ) : (
                <form onSubmit={submit} className="form" noValidate>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
                    Name
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      onBlur={() => handleBlur("name")}
                      type="text"
                      placeholder="Your full name"
                      aria-invalid={touched.name && !!errors.name}
                      aria-describedby={errors.name ? "name-error" : undefined}
                      style={touched.name && errors.name ? { borderColor: "var(--color-danger)" } : undefined}
                    />
                    {touched.name && errors.name && (
                      <span
                        id="name-error"
                        role="alert"
                        style={{
                          color: "var(--color-danger)",
                          fontSize: "var(--text-sm)",
                          marginTop: "var(--space-1)",
                        }}
                      >
                        {errors.name}
                      </span>
                    )}
                  </motion.label>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 }}>
                    Email
                    <input
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onBlur={() => handleBlur("email")}
                      type="email"
                      placeholder="you@company.com"
                      aria-invalid={touched.email && !!errors.email}
                      aria-describedby={errors.email ? "email-error" : undefined}
                      style={touched.email && errors.email ? { borderColor: "var(--color-danger)" } : undefined}
                    />
                    {touched.email && errors.email && (
                      <span
                        id="email-error"
                        role="alert"
                        style={{
                          color: "var(--color-danger)",
                          fontSize: "var(--text-sm)",
                          marginTop: "var(--space-1)",
                        }}
                      >
                        {errors.email}
                      </span>
                    )}
                  </motion.label>
                  <motion.label initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}>
                    Message
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onBlur={() => handleBlur("message")}
                      rows={5}
                      placeholder="Tell us about your requirements..."
                      aria-invalid={touched.message && !!errors.message}
                      aria-describedby={errors.message ? "message-error" : undefined}
                      style={{
                        resize: "vertical",
                        minHeight: 100,
                        padding: "10px 12px",
                        ...(touched.message && errors.message ? { borderColor: "var(--color-danger)" } : {}),
                      }}
                    />
                    {touched.message && errors.message && (
                      <span
                        id="message-error"
                        role="alert"
                        style={{
                          color: "var(--color-danger)",
                          fontSize: "var(--text-sm)",
                          marginTop: "var(--space-1)",
                        }}
                      >
                        {errors.message}
                      </span>
                    )}
                  </motion.label>

                  {submitError && (
                    <div
                      role="alert"
                      style={{
                        color: "var(--color-danger)",
                        fontSize: "var(--text-sm)",
                        padding: "var(--space-3)",
                        background: "var(--color-danger-subtle)",
                        borderRadius: "var(--radius-md)",
                      }}
                    >
                      {submitError}
                    </div>
                  )}

                  <motion.button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                    style={{ width: "100%", justifyContent: "center" }}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {loading ? (
                      <>
                        <Send size={16} style={{ opacity: 0.7 }} />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send size={16} />
                        Send message
                      </>
                    )}
                  </motion.button>
                </form>
              )}
            </div>
          </FadeIn>
        </div>
      </section>

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
