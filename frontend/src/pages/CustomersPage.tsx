import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { FadeIn, StaggerContainer, staggerItem } from "../components/animations";
import { api, unwrap } from "../lib/api";

type Customer = {
  id: string;
  customer_id: string;
  full_name: string;
  phone_number: string;
  region?: string;
  operator?: string;
  arpu?: number;
  churn_status: boolean;
  status: string;
};

type Paginated<T> = { items: T[]; total: number };

export function CustomersPage() {
  const [search, setSearch] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const params = search ? { search } : {};
    void unwrap<Paginated<Customer>>(api.get("/customers", { params }))
      .then((data) => {
        setCustomers(data.items);
        setTotal(data.total);
      })
      .catch(() => {
        setCustomers([]);
        setTotal(0);
      });
  }, [search]);

  return (
    <section className="page">
      <FadeIn>
        <div className="page-title">
          <h1>Customer Explorer</h1>
          <motion.div
            className="search-box"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            <Search size={16} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search customers" />
          </motion.div>
        </div>
      </FadeIn>

      <FadeIn delay={0.15}>
        <div className="table-panel">
          <div className="table-meta">{total} records</div>
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Phone</th>
                <th>Operator</th>
                <th>Region</th>
                <th>ARPU</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <StaggerContainer stagger={0.03}>
                {customers.map((customer) => (
                  <motion.tr key={customer.id} variants={staggerItem}>
                    <td>
                      <Link to={`/customers/${customer.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                        <strong style={{ color: "#1d8a8a" }}>{customer.full_name}</strong>
                      </Link>
                      <span>{customer.customer_id}</span>
                    </td>
                    <td>{customer.phone_number}</td>
                    <td>{customer.operator ?? "-"}</td>
                    <td>{customer.region ?? "-"}</td>
                    <td>${Number(customer.arpu ?? 0).toLocaleString()}</td>
                    <td><StatusPill value={customer.churn_status ? "Churned" : customer.status} /></td>
                  </motion.tr>
                ))}
              </StaggerContainer>
              {!customers.length ? (
                <tr>
                  <td colSpan={6} className="empty">No customers found</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </FadeIn>
    </section>
  );
}
