import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogOut, Settings, Bell } from "lucide-react";
import { useAuthStore } from "../../state/auth";
import { Breadcrumbs } from "../../components/Breadcrumbs";
import { MobileNav } from "../../components/MobileNav";

export function AdminTopbar() {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  return (
    <motion.header
      className="admin-topbar"
      initial={{ y: -64, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.2, duration: 0.4 }}
    >
      <div className="admin-topbar-left">
        <MobileNav>
          <div className="mobile-sidebar-brand">Telco Retain</div>
        </MobileNav>
        <Breadcrumbs />
      </div>
      <div className="admin-topbar-right">
        <div className="admin-user-info">
          <span className="admin-user-name">{user?.full_name ?? "Admin"}</span>
          <span className="admin-user-role">{user?.role?.name ?? "Super Admin"}</span>
        </div>
        <motion.button
          className="admin-icon-button"
          title="Notifications"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <Bell size={18} />
        </motion.button>
        <motion.button
          className="admin-icon-button"
          title="Settings"
          onClick={() => navigate("/admin/settings")}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <Settings size={18} />
        </motion.button>
        <motion.button
          className="admin-icon-button logout"
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
