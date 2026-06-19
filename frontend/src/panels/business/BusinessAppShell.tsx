import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { BusinessSidebar } from "./BusinessSidebar";
import { BusinessTopbar } from "./BusinessTopbar";

export function BusinessAppShell() {
  const location = useLocation();

  return (
    <div className="business-shell">
      <BusinessSidebar />
      <main className="business-main">
        <BusinessTopbar />
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="business-content"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
