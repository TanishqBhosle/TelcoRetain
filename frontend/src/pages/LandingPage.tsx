import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { motion, useInView, useMotionValue, useSpring, type Variants } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Cable,
  ChevronDown,
  Check,
  Target,
  Users,
  TrendingDown,
  Wallet,
  Activity,
  Shield,
  Zap,
  Layers,
  Play,
  Menu,
  X,
  Linkedin,
  Twitter,
  Github,
  Mail,
  Phone,
  MapPin,
  ChevronRight,
  LineChart,
  PieChart,
  RefreshCw,
  Globe,
  Lock,
  Clock,
} from "lucide-react";
import {
  LineChart as RechartsLine,
  Line,
  BarChart as RechartsBar,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";

/* ─── Types ─── */
type NavLink = { label: string; href: string };
type Feature = { icon: typeof BrainCircuit; title: string; description: string };
type Stat = { value: string; label: string; suffix: string };
type Step = { number: string; title: string; description: string };
type Testimonial = { quote: string; name: string; role: string; company: string };
type FAQ = { question: string; answer: string };
type FooterColumn = { title: string; links: { label: string; href: string }[] };

const easeArr: [number, number, number, number] = [0.25, 0.1, 0.25, 1];

/* ─── Data ─── */
const navLinks: NavLink[] = [
  { label: "Platform", href: "#platform" },
  { label: "Solutions", href: "#solutions" },
  { label: "Features", href: "#features" },
  { label: "Analytics", href: "#analytics" },
  { label: "Pricing", href: "/pricing" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const trustBadges = [
  { icon: Shield, label: "Enterprise Ready" },
  { icon: BrainCircuit, label: "Explainable AI" },
  { icon: Activity, label: "Real-Time Insights" },
  { icon: BarChart3, label: "Telecom Analytics" },
];

const stats: Stat[] = [
  { value: "150", label: "Customers Analyzed", suffix: "K+" },
  { value: "98", label: "Prediction Accuracy", suffix: "%" },
  { value: "30", label: "Reduction in Churn", suffix: "%" },
  { value: "50", label: "Revenue Protected", suffix: "M+" },
];

const features: Feature[] = [
  {
    icon: BrainCircuit,
    title: "Churn Prediction",
    description: "Predict customer churn with machine learning models achieving 98% accuracy across diverse telecom markets.",
  },
  {
    icon: Target,
    title: "Explainable AI",
    description: "Understand why customers leave with SHAP-based explanations and business-friendly reason codes.",
  },
  {
    icon: Layers,
    title: "Retention Recommendations",
    description: "Generate personalized retention offers — discounts, data bonuses, and loyalty rewards — automatically.",
  },
];

const steps: Step[] = [
  { number: "01", title: "Analyze Customer Behavior", description: "Ingest and process customer data — usage patterns, recharge history, network quality, and support interactions." },
  { number: "02", title: "Predict Churn Risk", description: "Ensemble ML models score every subscriber for churn probability with explainable AI insights." },
  { number: "03", title: "Generate Retention Strategy", description: "Rule-based engine creates personalized offers targeting at-risk customers with optimal incentive levels." },
  { number: "04", title: "Improve Customer Loyalty", description: "Track campaign performance, measure retention lift, and continuously improve prediction accuracy." },
];

const productTabs = [
  { id: "explorer", label: "Customer Explorer", icon: Users },
  { id: "analytics", label: "Analytics Dashboard", icon: BarChart3 },
  { id: "recommendations", label: "Recommendation Center", icon: Target },
  { id: "campaigns", label: "Campaign Manager", icon: Activity },
];

const testimonials: Testimonial[] = [
  { quote: "TelcoRetain helped us reduce churn by 30% in the first quarter. The explainable AI is a game-changer for our retention team.", name: "Rajesh Mehta", role: "VP of Customer Experience", company: "Bharti Airtel" },
  { quote: "We finally understand why customers leave. The SHAP explanations give our team actionable insights they can actually use.", name: "Priya Sharma", role: "Head of Retention", company: "Vodafone Idea" },
  { quote: "The platform's real-time analytics and campaign management capabilities are unmatched in the telecom analytics space.", name: "Ankit Patel", role: "Chief Marketing Officer", company: "Jio Platforms" },
];

const faqs: FAQ[] = [
  { question: "How does TelcoRetain integrate with existing telecom systems?", answer: "TelcoRetain provides REST APIs, batch data import pipelines, and real-time streaming connectors for CDRs, billing systems, CRM platforms, and network monitoring tools." },
  { question: "What data do I need to get started?", answer: "You need customer demographic data, usage patterns, recharge history, network quality metrics, and support ticket logs. Our onboarding team helps map and transform your data." },
  { question: "How accurate are the churn predictions?", answer: "Our ensemble models achieve 83-98% AUC-ROC depending on data quality. Models are trained on your specific customer base and continuously retrained for optimal performance." },
  { question: "Is the platform compliant with data privacy regulations?", answer: "Yes. TelcoRetain is GDPR, CCPA, and TRAI compliant. All data is encrypted at rest and in transit, with role-based access controls and full audit logging." },
  { question: "Can I export predictions and reports?", answer: "Yes. All predictions, explanations, and analytics dashboards can be exported as CSV, PDF, or accessed via API for integration with your BI tools." },
  { question: "What kind of support do you offer?", answer: "We offer 24/7 enterprise support with dedicated account managers, technical onboarding, and custom integration assistance for all paid plans." },
];

const footerColumns: FooterColumn[] = [
  {
    title: "Platform",
    links: [
      { label: "Churn Prediction", href: "#" },
      { label: "Explainable AI", href: "#" },
      { label: "Retention Offers", href: "#" },
      { label: "Campaign Management", href: "#" },
      { label: "Analytics", href: "#" },
    ],
  },
  {
    title: "Solutions",
    links: [
      { label: "Telecom Operators", href: "#" },
      { label: "Retention Teams", href: "#" },
      { label: "Marketing Teams", href: "#" },
      { label: "CRM Teams", href: "#" },
      { label: "Business Executives", href: "#" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "#" },
      { label: "API Reference", href: "#" },
      { label: "Case Studies", href: "#" },
      { label: "Blog", href: "#" },
      { label: "Help Center", href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About Us", href: "/about" },
      { label: "Careers", href: "#" },
      { label: "Partners", href: "#" },
      { label: "Press Kit", href: "#" },
      { label: "Contact", href: "/contact" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Cookie Policy", href: "#" },
      { label: "GDPR", href: "#" },
      { label: "SLA", href: "#" },
    ],
  },
];

const socialLinks = [
  { icon: Linkedin, href: "#" },
  { icon: Twitter, href: "#" },
  { icon: Github, href: "#" },
];

const companyLogos = [
  "Airtel", "Jio", "Vi", "BSNL", "Tata", "Reliance"
];

/* ─── Chart data ─── */
const churnTrendData = [
  { month: "Jan", churnRate: 4.2, industryAvg: 5.1 },
  { month: "Feb", churnRate: 3.8, industryAvg: 5.0 },
  { month: "Mar", churnRate: 3.5, industryAvg: 4.9 },
  { month: "Apr", churnRate: 3.1, industryAvg: 4.8 },
  { month: "May", churnRate: 2.8, industryAvg: 4.7 },
  { month: "Jun", churnRate: 2.4, industryAvg: 4.6 },
  { month: "Jul", churnRate: 2.1, industryAvg: 4.5 },
];

const revenueData = [
  { month: "Jan", retained: 8.2, atRisk: 2.1 },
  { month: "Feb", retained: 8.5, atRisk: 1.9 },
  { month: "Mar", retained: 8.8, atRisk: 1.7 },
  { month: "Apr", retained: 9.1, atRisk: 1.5 },
  { month: "May", retained: 9.4, atRisk: 1.3 },
  { month: "Jun", retained: 9.6, atRisk: 1.2 },
  { month: "Jul", retained: 9.8, atRisk: 1.0 },
];

const operatorData = [
  { name: "Operator A", churn: 2.1 },
  { name: "Operator B", churn: 3.4 },
  { name: "Operator C", churn: 4.8 },
  { name: "Operator D", churn: 2.9 },
  { name: "Operator E", churn: 5.2 },
];

/* ─── Animation Variants ─── */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: easeArr } },
};

const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: easeArr },
  }),
};

/* ─── Animated Counter ─── */
function AnimatedCounter({ from, to, suffix, duration = 2 }: { from: number; to: number; suffix: string; duration?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const motionValue = useMotionValue(from);
  const spring = useSpring(motionValue, { stiffness: 50, damping: 20 });
  const [display, setDisplay] = useState(from.toFixed(0));

  useEffect(() => {
    if (inView) {
      motionValue.set(to);
      const unsubscribe = spring.on("change", (v) => {
        setDisplay(Math.round(v).toLocaleString());
      });
      return unsubscribe;
    }
  }, [inView, to, motionValue, spring]);

  return <span ref={ref}>{display}{suffix}</span>;
}

/* ─── Magnetic Button ─── */
function MagneticButton({ children, href, variant = "primary", onClick }: {
  children: React.ReactNode;
  href?: string;
  variant?: "primary" | "secondary" | "outline";
  onClick?: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setPosition({ x: x * 0.3, y: y * 0.3 });
  };

  const handleLeave = () => setPosition({ x: 0, y: 0 });

  const variants = {
    primary: "landing-btn-primary",
    secondary: "landing-btn-secondary",
    outline: "landing-btn-outline",
  };

  if (href && !href.startsWith("#")) {
    return (
      <motion.div
        ref={ref}
        onMouseMove={handleMouse}
        onMouseLeave={handleLeave}
        animate={{ x: position.x, y: position.y }}
        transition={{ type: "spring", stiffness: 150, damping: 15 }}
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
      >
        <Link to={href} className={`landing-btn ${variants[variant]}`}>
          {children}
        </Link>
      </motion.div>
    );
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 150, damping: 15 }}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
    >
      <a href={href || "#"} className={`landing-btn ${variants[variant]}`}>
        {children}
      </a>
    </motion.div>
  );
}

/* ─── Parallax Card ─── */
function ParallaxCard({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [rotate, setRotate] = useState({ x: 0, y: 0 });

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setRotate({ x: -y * 4, y: x * 4 });
  };

  const handleLeave = () => setRotate({ x: 0, y: 0 });

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      animate={{ rotateX: rotate.x, rotateY: rotate.y }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      className={className}
      style={{ perspective: 1000 }}
    >
      {children}
    </motion.div>
  );
}

/* ─── Navbar ─── */
function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      className={`landing-navbar ${scrolled ? "navbar-scrolled" : ""}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          <Cable size={22} />
          <span>TELCORETAIN</span>
        </Link>

        <div className={`navbar-links ${mobileOpen ? "navbar-mobile-open" : ""}`}>
          {navLinks.map((link) => {
            const isRouter = link.href.startsWith("/");
            if (isRouter) {
              return (
                <Link key={link.label} to={link.href} className="navbar-link" onClick={() => setMobileOpen(false)}>
                  {link.label}
                </Link>
              );
            }
            return (
              <a key={link.label} href={link.href} className="navbar-link" onClick={() => setMobileOpen(false)}>
                {link.label}
              </a>
            );
          })}
        </div>

        <div className="navbar-actions">
          <Link to="/signin" className="navbar-login">Sign in</Link>
          <MagneticButton href="/signup" variant="primary">Request Demo <ArrowRight size={16} /></MagneticButton>
          <button className="navbar-mobile-toggle" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
    </motion.nav>
  );
}

/* ─── Particles ─── */
function Particles() {
  return (
    <div className="particles-container" aria-hidden="true">
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * 4 + 2}px`,
            height: `${Math.random() * 4 + 2}px`,
            opacity: Math.random() * 0.3 + 0.1,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{
            duration: Math.random() * 6 + 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: Math.random() * 3,
          }}
        />
      ))}
    </div>
  );
}

/* ─── Dashboard Mockup ─── */
function DashboardMockup() {
  return (
    <motion.div
      className="dashboard-mockup"
      initial={{ opacity: 0, y: 60, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="dashboard-header">
        <div className="dashboard-dots">
          <span /><span /><span />
        </div>
        <span className="dashboard-title">Churn Intelligence Dashboard</span>
      </div>
      <div className="dashboard-body">
        <div className="dashboard-metrics">
          <ParallaxCard>
            <div className="dashboard-metric-card card-1">
              <span className="metric-label">Churn Rate</span>
              <strong className="metric-value">2.1%</strong>
              <span className="metric-change positive">↓ 12.5% MoM</span>
            </div>
          </ParallaxCard>
          <ParallaxCard>
            <div className="dashboard-metric-card card-2">
              <span className="metric-label">High Risk</span>
              <strong className="metric-value">847</strong>
              <span className="metric-change negative">↑ 3.2%</span>
            </div>
          </ParallaxCard>
          <ParallaxCard>
            <div className="dashboard-metric-card card-3">
              <span className="metric-label">Revenue at Risk</span>
              <strong className="metric-value">₹2.4Cr</strong>
              <span className="metric-change negative">↓ 8.1%</span>
            </div>
          </ParallaxCard>
          <ParallaxCard>
            <div className="dashboard-metric-card card-4">
              <span className="metric-label">Campaign ROI</span>
              <strong className="metric-value">384%</strong>
              <span className="metric-change positive">↑ 22.3%</span>
            </div>
          </ParallaxCard>
        </div>
        <div className="dashboard-charts">
          <div className="dashboard-chart chart-large">
            <span className="chart-title">Churn Trend</span>
            <ResponsiveContainer width="100%" height={150}>
              <AreaChart data={churnTrendData}>
                <defs>
                  <linearGradient id="churnGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#AFD2FA" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#AFD2FA" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} domain={[0, 6]} />
                <Tooltip
                  contentStyle={{
                    background: "#182350",
                    border: "1px solid rgba(175, 210, 250, 0.2)",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Area type="monotone" dataKey="industryAvg" stroke="#B9915E" strokeWidth={1.5} fill="none" strokeDasharray="4 4" />
                <Area type="monotone" dataKey="churnRate" stroke="#AFD2FA" strokeWidth={2} fill="url(#churnGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="dashboard-chart chart-small">
            <span className="chart-title">Revenue (₹Cr)</span>
            <ResponsiveContainer width="100%" height={150}>
              <RechartsBar data={revenueData} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "#182350",
                    border: "1px solid rgba(175, 210, 250, 0.2)",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="retained" fill="#AFD2FA" radius={[3, 3, 0, 0]} />
                <Bar dataKey="atRisk" fill="#B9915E" radius={[3, 3, 0, 0]} />
              </RechartsBar>
            </ResponsiveContainer>
          </div>
          <div className="dashboard-chart chart-small">
            <span className="chart-title">Operator Churn %</span>
            <ResponsiveContainer width="100%" height={150}>
              <RechartsBar data={operatorData} layout="vertical" margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} domain={[0, 6]} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "#182350",
                    border: "1px solid rgba(175, 210, 250, 0.2)",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="churn" fill="#AFD2FA" radius={[0, 3, 3, 0]} />
              </RechartsBar>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Sections ─── */

// Hero
function HeroSection() {
  return (
    <section className="section-hero" id="platform">
      <Particles />
      <div className="hero-grid">
        <motion.div className="hero-content" variants={containerVariants} initial="hidden" animate="visible">
          <motion.div className="hero-badge" variants={itemVariants}>
            <Zap size={14} />
            <span>Telecom Customer Retention Intelligence Platform</span>
          </motion.div>
          <motion.h1 className="hero-headline" variants={itemVariants}>
            Predict Customer Churn<br />
            <span className="hero-highlight">Before It Happens</span>
          </motion.h1>
          <motion.p className="hero-subheadline" variants={itemVariants}>
            AI-powered telecom customer retention platform helping operators reduce churn, improve customer loyalty, maximize revenue, and make data-driven retention decisions.
          </motion.p>
          <motion.div className="hero-actions" variants={itemVariants}>
            <MagneticButton href="/signup" variant="primary">
              Request Demo <ArrowRight size={18} />
            </MagneticButton>
            <MagneticButton href="#tour" variant="secondary">
              <Play size={18} /> Watch Platform Tour
            </MagneticButton>
          </motion.div>
          <motion.div className="hero-trust" variants={itemVariants}>
            {trustBadges.map((badge) => (
              <div key={badge.label} className="trust-badge">
                <badge.icon size={14} />
                <span>{badge.label}</span>
              </div>
            ))}
          </motion.div>
        </motion.div>

        <div className="hero-visual">
          <DashboardMockup />
        </div>
      </div>
    </section>
  );
}

// Stats
function StatsSection() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section className="section-stats" ref={ref}>
      <div className="section-inner">
        <motion.div
          className="stats-grid"
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          variants={containerVariants}
        >
          {stats.map((stat, i) => (
            <motion.div key={stat.label} className="stat-card" variants={itemVariants}>
              <strong className="stat-value">
                <AnimatedCounter from={0} to={parseInt(stat.value)} suffix={stat.suffix} />
              </strong>
              <span className="stat-label">{stat.label}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

// Social Proof
function SocialProofSection() {
  return (
    <section className="section-social-proof">
      <div className="section-inner">
        <motion.h2
          className="section-subtitle"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Trusted by Telecom Teams Worldwide
        </motion.h2>
        <motion.div
          className="logos-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
        >
          {companyLogos.map((logo, i) => (
            <motion.div key={logo} className="logo-item" variants={itemVariants}>
              <span>{logo}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

// Features
function FeaturesSection() {
  return (
    <section className="section-features" id="features">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">Intelligent Retention, Built for Telecom</h2>
          <p className="section-description">
            From prediction to action — a complete retention intelligence stack powered by machine learning.
          </p>
        </motion.div>
        <div className="features-grid">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              className="feature-card"
              custom={i}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-60px" }}
              variants={fadeUpVariants}
              whileHover={{ y: -6, boxShadow: "0 20px 48px rgba(24, 35, 80, 0.1)" }}
              transition={{ duration: 0.25 }}
            >
              <div className="feature-icon">
                <feature.icon size={24} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// How It Works
function HowItWorksSection() {
  return (
    <section className="section-how-it-works" id="solutions">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">How It Works</h2>
          <p className="section-description">
            Four steps to transform your customer retention strategy.
          </p>
        </motion.div>
        <div className="steps-timeline">
          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              className="step-item"
              initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ delay: i * 0.15, duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
            >
              <div className="step-number">{step.number}</div>
              <div className="step-content">
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="step-connector">
                  <ChevronDown size={20} />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Product Showcase
function ProductShowcaseSection() {
  const [activeTab, setActiveTab] = useState("explorer");

  const tabContent: Record<string, { title: string; description: string; features: string[] }> = {
    explorer: {
      title: "Customer Explorer",
      description: "Unified 360° customer profiles with usage patterns, recharge history, support tickets, and activity timeline.",
      features: ["Demographic data and account details", "Usage patterns and recharge history", "Support ticket history", "Activity timeline and events"],
    },
    analytics: {
      title: "Analytics Dashboard",
      description: "Real-time KPIs, churn trends, revenue at risk, regional analysis, and operator exposure metrics.",
      features: ["Churn trend analysis", "Revenue impact tracking", "Regional performance", "Operator benchmarking"],
    },
    recommendations: {
      title: "Recommendation Center",
      description: "AI-powered retention offer engine that generates personalized incentives for at-risk customers.",
      features: ["Personalized discount offers", "Data bonus recommendations", "Loyalty reward programs", "A/B testing capabilities"],
    },
    campaigns: {
      title: "Campaign Manager",
      description: "Create, target, and track retention campaigns with real-time conversion analytics and ROI measurement.",
      features: ["Campaign creation wizard", "Smart customer targeting", "Multi-channel delivery", "Conversion analytics"],
    },
  };

  const content = tabContent[activeTab];

  return (
    <section className="section-product">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">Explore the Platform</h2>
          <p className="section-description">
            Everything your team needs to predict, prevent, and manage customer churn.
          </p>
        </motion.div>

        <div className="product-tabs">
          {productTabs.map((tab) => (
            <button
              key={tab.id}
              className={`product-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <motion.div
          className="product-content"
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="product-text">
            <h3>{content.title}</h3>
            <p>{content.description}</p>
            <ul className="product-features">
              {content.features.map((f) => (
                <li key={f}>
                  <Check size={16} />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <MagneticButton href="/signup" variant="outline">
              Learn More <ChevronRight size={16} />
            </MagneticButton>
          </div>
          <div className="product-visual">
            <div className="product-mockup">
              <div className="mockup-bar">
                <div className="mockup-dots"><span /><span /><span /></div>
                <span>{content.title}</span>
              </div>
              <div className="mockup-body">
                <div className="mockup-row"><div className="mockup-label" /><div className="mockup-bar-chart"><div /><div /><div /></div></div>
                <div className="mockup-row"><div className="mockup-label" /><div className="mockup-line" /></div>
                <div className="mockup-row"><div className="mockup-label" /><div className="mockup-grid"><div /><div /><div /><div /></div></div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Analytics
function AnalyticsSection() {
  return (
    <section className="section-analytics" id="analytics">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">Enterprise Analytics</h2>
          <p className="section-description">
            Comprehensive analytics to understand every dimension of customer churn.
          </p>
        </motion.div>

        <div className="analytics-grid">
          <motion.div
            className="analytics-card analytics-card-large"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="analytics-card-header">
              <LineChart size={20} />
              <span>Churn Trends</span>
            </div>
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={churnTrendData}>
                  <defs>
                    <linearGradient id="analyticsChurn" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#182350" stopOpacity={0.15} />
                      <stop offset="100%" stopColor="#182350" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E8E4D8" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="churnRate" stroke="#182350" strokeWidth={2} fill="url(#analyticsChurn)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div
            className="analytics-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="analytics-card-header">
              <Wallet size={20} />
              <span>Revenue Impact</span>
            </div>
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height={200}>
                <RechartsBar data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E8E4D8" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="retained" fill="#182350" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="atRisk" fill="#B9915E" radius={[4, 4, 0, 0]} />
                </RechartsBar>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div
            className="analytics-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="analytics-card-header">
              <Globe size={20} />
              <span>Operator Analysis</span>
            </div>
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height={200}>
                <RechartsBar data={operatorData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E8E4D8" />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: "#7C7A72", fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="churn" fill="#182350" radius={[0, 4, 4, 0]} />
                </RechartsBar>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div
            className="analytics-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <div className="analytics-card-header">
              <Users size={20} />
              <span>Customer Segmentation</span>
            </div>
            <div className="analytics-segmentation">
              {[
                { label: "Low Risk", value: 62, color: "#16A34A" },
                { label: "Medium Risk", value: 23, color: "#B9915E" },
                { label: "High Risk", value: 15, color: "#DC2626" },
              ].map((seg) => (
                <div key={seg.label} className="segment-row">
                  <div className="segment-info">
                    <span className="segment-dot" style={{ background: seg.color }} />
                    <span className="segment-label">{seg.label}</span>
                  </div>
                  <div className="segment-bar-track">
                    <motion.div
                      className="segment-bar-fill"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${seg.value}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
                      style={{ background: seg.color }}
                    />
                  </div>
                  <span className="segment-value">{seg.value}%</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// Testimonials
function TestimonialsSection() {
  return (
    <section className="section-testimonials">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">Trusted by Industry Leaders</h2>
          <p className="section-description">
            See how telecom teams are transforming retention with TelcoRetain.
          </p>
        </motion.div>

        <div className="testimonials-grid">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              className="testimonial-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15, duration: 0.5 }}
              whileHover={{ y: -4, boxShadow: "0 20px 48px rgba(24, 35, 80, 0.08)" }}
            >
              <div className="testimonial-quote">"{t.quote}"</div>
              <div className="testimonial-author">
                <div className="testimonial-avatar">
                  {t.name.split(" ").map(n => n[0]).join("")}
                </div>
                <div>
                  <strong>{t.name}</strong>
                  <span>{t.role}, {t.company}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// FAQ
function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section className="section-faq">
      <div className="section-inner">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="section-title">Frequently Asked Questions</h2>
          <p className="section-description">
            Everything you need to know about TelcoRetain.
          </p>
        </motion.div>

        <div className="faq-list">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              className={`faq-item ${openIndex === i ? "faq-open" : ""}`}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
            >
              <button className="faq-question" onClick={() => setOpenIndex(openIndex === i ? null : i)}>
                <span>{faq.question}</span>
                <ChevronDown size={18} className={`faq-chevron ${openIndex === i ? "rotated" : ""}`} />
              </button>
              <motion.div
                className="faq-answer"
                initial={false}
                animate={{
                  height: openIndex === i ? "auto" : 0,
                  opacity: openIndex === i ? 1 : 0,
                }}
                transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
              >
                <p>{faq.answer}</p>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Final CTA
function FinalCTASection() {
  return (
    <section className="section-final-cta">
      <div className="section-inner">
        <motion.div
          className="final-cta-content"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="final-cta-headline">Reduce Customer Churn Before It Impacts Revenue</h2>
          <p className="final-cta-text">
            Join leading telecom operators who trust TelcoRetain to protect their revenue and grow customer loyalty.
          </p>
          <div className="final-cta-actions">
            <MagneticButton href="/signup" variant="primary">
              Request Demo <ArrowRight size={18} />
            </MagneticButton>
            <MagneticButton href="/signup" variant="secondary">
              Get Started <ArrowRight size={18} />
            </MagneticButton>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Footer
function FooterSection() {
  return (
    <footer className="landing-footer-comprehensive">
      <div className="section-inner">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="navbar-logo" style={{ marginBottom: 16 }}>
              <Cable size={22} />
              <span>TELCORETAIN</span>
            </div>
            <p className="footer-tagline">
              AI-powered telecom customer retention intelligence platform.
            </p>
            <div className="footer-social">
              {socialLinks.map((link, i) => (
                <a key={i} href={link.href} className="footer-social-link" aria-label={`Social link ${i + 1}`}>
                  <link.icon size={18} />
                </a>
              ))}
            </div>
          </div>

          {footerColumns.map((col) => (
            <div key={col.title} className="footer-column">
              <h4>{col.title}</h4>
              <ul>
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a href={link.href}>{link.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="footer-bottom">
          <div className="footer-contact">
            <div className="footer-contact-item">
              <Mail size={14} />
              <span>hello@telcoretain.com</span>
            </div>
            <div className="footer-contact-item">
              <Phone size={14} />
              <span>+91 1800-123-4567</span>
            </div>
            <div className="footer-contact-item">
              <MapPin size={14} />
              <span>Mumbai, India</span>
            </div>
          </div>
          <div className="footer-legal">
            <span>&copy; {new Date().getFullYear()} TelcoRetain. All rights reserved.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

/* ─── Main Landing Page ─── */
export function LandingPage() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="landing-page">
      <Navbar />
      <HeroSection />
      <StatsSection />
      <SocialProofSection />
      <FeaturesSection />
      <HowItWorksSection />
      <ProductShowcaseSection />
      <AnalyticsSection />
      <TestimonialsSection />
      <FAQSection />
      <FinalCTASection />
      <FooterSection />
    </div>
  );
}
