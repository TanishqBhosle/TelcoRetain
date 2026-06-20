import { useEffect } from "react";
import { Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useAuthStore } from "./state/auth";
import { api, unwrap } from "./lib/api";
import { AdminAppShell } from "./panels/admin/AdminAppShell";
import { BusinessAppShell } from "./panels/business/BusinessAppShell";
import { RoleGuard, isAdminRole } from "./components/RoleGuard";

import { AdminDashboard } from "./panels/admin/pages/AdminDashboard";
import { UserManagement } from "./panels/admin/pages/UserManagement";
import { DatasetManagement } from "./panels/admin/pages/DatasetManagement";
import { ModelManagement } from "./panels/admin/pages/ModelManagement";
import { AuditLogs } from "./panels/admin/pages/AuditLogs";

import { BusinessDashboard } from "./panels/business/pages/BusinessDashboard";
import { CustomerExplorer } from "./panels/business/pages/CustomerExplorer";
import { CustomerProfile } from "./panels/business/pages/CustomerProfile";
import { ChurnPrediction } from "./panels/business/pages/ChurnPrediction";
import { ShapAnalysis } from "./panels/business/pages/ShapAnalysis";
import { RecommendationCenter } from "./panels/business/pages/RecommendationCenter";
import { AnalyticsDashboard } from "./panels/business/pages/AnalyticsDashboard";

import { LandingPage } from "./pages/LandingPage";
import { AboutPage } from "./pages/AboutPage";
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

function RoleRedirect() {
  const user = useAuthStore((state) => state.user);
  const dest = isAdminRole(user?.role?.name) ? "/admin/dashboard" : "/app/dashboard";
  return <Navigate to={dest} replace />;
}

export default function App() {
  return (
    <Routes>
      {/* Public marketing pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />

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
          <Route path="datasets" element={<DatasetManagement />} />
          <Route path="models" element={<ModelManagement />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="audit-logs" element={<AuditLogs />} />
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
          <Route path="shap" element={<ShapAnalysis />} />
          <Route path="recommendations" element={<RecommendationCenter />} />
          <Route path="analytics" element={<AnalyticsDashboard />} />
        </Route>

        {/* Redirect root to appropriate panel */}
        <Route path="/dashboard" element={<RoleRedirect />} />
      </Route>
    </Routes>
  );
}

