import { useEffect } from "react";
import { Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useAuthStore } from "./state/auth";
import { api, unwrap } from "./lib/api";
import { AdminAppShell } from "./panels/admin/AdminAppShell";
import { BusinessAppShell } from "./panels/business/BusinessAppShell";
import { RoleGuard, isAdminRole } from "./components/RoleGuard";

import { AdminDashboard } from "./panels/admin/pages/AdminDashboard";
import { UserManagement } from "./panels/admin/pages/UserManagement";
import { RolesPermissions } from "./panels/admin/pages/RolesPermissions";
import { DatasetManagement } from "./panels/admin/pages/DatasetManagement";
import { ModelRegistry } from "./panels/admin/pages/ModelRegistry";
import { ModelMonitoring } from "./panels/admin/pages/ModelMonitoring";
import { SystemSettings } from "./panels/admin/pages/SystemSettings";
import { AuditLogs } from "./panels/admin/pages/AuditLogs";
import { APIMonitoring } from "./panels/admin/pages/APIMonitoring";
import { DatabaseHealth } from "./panels/admin/pages/DatabaseHealth";
import { SecurityCenter } from "./panels/admin/pages/SecurityCenter";
import { NotificationSettings } from "./panels/admin/pages/NotificationSettings";

import { BusinessDashboard } from "./panels/business/pages/BusinessDashboard";
import { CustomerExplorer } from "./panels/business/pages/CustomerExplorer";
import { CustomerProfile } from "./panels/business/pages/CustomerProfile";
import { ChurnPrediction } from "./panels/business/pages/ChurnPrediction";
import { ExplainableAI } from "./panels/business/pages/ExplainableAI";
import { RecommendationCenter } from "./panels/business/pages/RecommendationCenter";
import { CampaignManagement } from "./panels/business/pages/CampaignManagement";
import { AnalyticsDashboard } from "./panels/business/pages/AnalyticsDashboard";
import { Reports } from "./panels/business/pages/Reports";
import { ProfileSettings } from "./panels/business/pages/ProfileSettings";

import { LandingPage } from "./pages/LandingPage";
import { AboutPage } from "./pages/AboutPage";
import { PricingPage } from "./pages/PricingPage";
import { ContactPage } from "./pages/ContactPage";
import { SignInPage } from "./pages/SignInPage";
import { SignUpPage } from "./pages/SignUpPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";
import { PasswordResetRequestPage } from "./pages/PasswordResetRequestPage";
import { PasswordResetConfirmPage } from "./pages/PasswordResetConfirmPage";
import { PostLogoutPage } from "./pages/PostLogoutPage";

type User = {
  id: string;
  email: string;
  full_name: string;
  role?: { name: string };
};

function Protected() {
  const token = useAuthStore((state) => state.accessToken);
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const navigate = useNavigate();

  useEffect(() => {
    if (token && !user) {
      unwrap<User>(api.get("/auth/me"))
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {});
    }
  }, [token, user, setUser]);

  if (!token) {
    return <Navigate to="/signin" replace />;
  }

  if (token && !user) {
    return null;
  }

  return <Outlet />;
}

function UnauthorizedPage() {
  return (
    <div className="unauthorized-page">
      <h1>403 - Unauthorized</h1>
      <p>You don't have permission to access this page.</p>
      <a href="/signin">Return to Sign In</a>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* Public marketing pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/contact" element={<ContactPage />} />

      {/* Auth pages */}
      <Route path="/signin" element={<SignInPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/password-reset" element={<PasswordResetRequestPage />} />
      <Route path="/password-reset/confirm" element={<PasswordResetConfirmPage />} />
      <Route path="/post-logout" element={<PostLogoutPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Protected routes */}
      <Route element={<Protected />}>
        {/* Admin Panel */}
        <Route
          path="/admin"
          element={
            <RoleGuard allowedRoles={["Super Admin", "Admin"]}>
              <AdminAppShell />
            </RoleGuard>
          }
        >
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="roles" element={<RolesPermissions />} />
          <Route path="datasets" element={<DatasetManagement />} />
          <Route path="models" element={<ModelRegistry />} />
          <Route path="model-monitoring" element={<ModelMonitoring />} />
          <Route path="settings" element={<SystemSettings />} />
          <Route path="audit-logs" element={<AuditLogs />} />
          <Route path="api-monitoring" element={<APIMonitoring />} />
          <Route path="database" element={<DatabaseHealth />} />
          <Route path="security" element={<SecurityCenter />} />
          <Route path="notifications" element={<NotificationSettings />} />
        </Route>

        {/* Business Panel */}
        <Route
          path="/app"
          element={
            <RoleGuard
              allowedRoles={[
                "Retention Manager",
                "Marketing Manager",
                "Business Analyst",
                "Customer Support Executive",
                "Executive Viewer",
              ]}
            >
              <BusinessAppShell />
            </RoleGuard>
          }
        >
          <Route path="dashboard" element={<BusinessDashboard />} />
          <Route path="customers" element={<CustomerExplorer />} />
          <Route path="customers/:id" element={<CustomerProfile />} />
          <Route path="predict" element={<ChurnPrediction />} />
          <Route path="explain" element={<ExplainableAI />} />
          <Route path="recommendations" element={<RecommendationCenter />} />
          <Route path="campaigns" element={<CampaignManagement />} />
          <Route path="analytics" element={<AnalyticsDashboard />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<ProfileSettings />} />
        </Route>

        {/* Redirect root to appropriate panel */}
        <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
