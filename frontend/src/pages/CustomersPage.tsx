import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
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
      <div className="page-title">
        <h1>Customer Explorer</h1>
        <div className="search-box">
          <Search size={16} />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search customers" />
        </div>
      </div>
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
            {customers.map((customer) => (
              <tr key={customer.id}>
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
              </tr>
            ))}
            {!customers.length ? (
              <tr>
                <td colSpan={6} className="empty">No customers found</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
