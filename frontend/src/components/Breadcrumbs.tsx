import { useLocation } from "react-router-dom";

const MAX_LEVELS = 4;

const labelMap: Record<string, string> = {
  app: "Business",
  admin: "Admin",
  dashboard: "Dashboard",
  customers: "Customers",
  predict: "Churn Prediction",
  explain: "Explainable AI",
  recommendations: "Recommendations",
  campaigns: "Campaigns",
  analytics: "Analytics",
  reports: "Reports",
  settings: "Settings",
  users: "User Management",
  roles: "Roles & Permissions",
  datasets: "Datasets",
  models: "Model Registry",
  "model-monitoring": "Model Monitoring",
  "audit-logs": "Audit Logs",
  "api-monitoring": "API Monitoring",
  database: "Database Health",
  security: "Security Center",
  notifications: "Notifications",
};

export function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  const crumbs = segments.map((seg) => labelMap[seg] ?? seg);

  const display =
    crumbs.length > MAX_LEVELS
      ? [crumbs[0], "...", ...crumbs.slice(-2)]
      : crumbs;

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {display.map((crumb, i) => (
        <span key={i} className="breadcrumb-item">
          {i > 0 && <span className="breadcrumb-sep">/</span>}
          <span>{crumb}</span>
        </span>
      ))}
    </nav>
  );
}
