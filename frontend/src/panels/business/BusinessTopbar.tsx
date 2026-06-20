import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogOut, Bell, User } from "lucide-react";
import { useAuthStore } from "../../state/auth";
import { Breadcrumbs } from "../../components/Breadcrumbs";
import { MobileNav } from "../../components/MobileNav";
import { ThemeToggle } from "../../components/ThemeToggle";

export function BusinessTopbar() {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  return (
    <motion.header
      className="business-topbar"
      initial={{ y: -64, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.2, duration: 0.4 }}
    >
      <div className="business-topbar-left">
        <MobileNav>
          <div className="mobile-sidebar-brand">Telco Retain</div>
        </MobileNav>
        <Breadcrumbs />
      </div>
      <div className="business-topbar-right">
        <div className="business-user-info">
          <span className="business-user-name">{user?.full_name ?? "User"}</span>
          <span className="business-user-role">{user?.role?.name ?? "Retention Manager"}</span>
        </div>
        <ThemeToggle />
        <motion.button
          className="business-icon-button"
          title="Notifications"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <Bell size={18} />
        </motion.button>
        <motion.button
          className="business-icon-button"
          title="Profile"
          onClick={() => navigate("/app/settings")}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <User size={18} />
        </motion.button>
        <motion.button
          className="business-icon-button logout"
          title="Log out"
          onClick={() => {
            logout();
            navigate("/post-logout");
          }}
          whileHover={{ scale: 1.1, backgroundColor: "#ffe3e7" }}
          whileTap={{ scale: 0.9 }}
        >
          <LogOut size={18} />
        </motion.button>
      </div>
    </motion.header>
  );
}
