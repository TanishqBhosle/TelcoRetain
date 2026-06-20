import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { motion } from "framer-motion";

export function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "light";
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.setAttribute("data-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <motion.button
      className="business-icon-button theme-toggle-btn"
      title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
      onClick={toggleTheme}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--color-neutral-100)",
        border: "none",
        borderRadius: "var(--radius-md)",
        padding: "8px",
        cursor: "pointer",
        color: "var(--color-neutral-600)",
      }}
    >
      {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
    </motion.button>
  );
}
