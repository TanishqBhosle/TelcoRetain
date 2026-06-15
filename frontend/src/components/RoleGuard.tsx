import { Navigate } from "react-router-dom";
import { useAuthStore } from "../state/auth";

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
  redirectPath?: string;
}

export function RoleGuard({ allowedRoles, children, redirectPath = "/unauthorized" }: RoleGuardProps) {
  const user = useAuthStore((state) => state.user);

  if (!user?.role?.name || !allowedRoles.includes(user.role.name)) {
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
}

export function isAdminRole(roleName: string | undefined): boolean {
  return roleName === "Super Admin" || roleName === "Admin";
}

export function isBusinessRole(roleName: string | undefined): boolean {
  const businessRoles = [
    "Retention Manager",
    "Marketing Manager",
    "Business Analyst",
    "Customer Support Executive",
    "Executive Viewer",
  ];
  return businessRoles.includes(roleName ?? "");
}

export function getPanelForRole(roleName: string | undefined): "/admin" | "/app" {
  return isAdminRole(roleName) ? "/admin" : "/app";
}
