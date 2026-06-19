import { LucideIcon } from "lucide-react";
import { NavLink } from "react-router-dom";

interface NavItem {
  to: string;
  icon: LucideIcon;
  label: string;
}

interface SidebarGroupProps {
  label: string;
  items: NavItem[];
  itemClassName?: string;
}

export function SidebarGroup({ label, items, itemClassName = "nav-item" }: SidebarGroupProps) {
  return (
    <div className="sidebar-group">
      <span className="sidebar-group-label">{label}</span>
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `${itemClassName} ${isActive ? "active" : ""}`
          }
        >
          <item.icon size={18} />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </div>
  );
}
