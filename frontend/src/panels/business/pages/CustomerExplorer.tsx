import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, Search, Filter, Eye, BrainCircuit, ChevronLeft, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api, unwrap } from "../../../lib/api";

type Customer = {
  id: string;
  customer_id: string;
  full_name: string;
  email: string;
  phone_number: string;
  operator: string;
  region: string;
  tenure_months: number;
  monthly_charges: number;
  churn_status: string;
};

export function CustomerExplorer() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [operator, setOperator] = useState("");
  const [riskLevel, setRiskLevel] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({
      page: page.toString(),
      limit: "20",
      ...(search && { search }),
      ...(operator && { operator }),
      ...(riskLevel && { risk_level: riskLevel }),
    });
    unwrap<{ items: Customer[]; total: number }>(api.get(`/customers?${params}`))
      .then((data) => {
        setCustomers(data.items || []);
        setTotal(data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search, operator, riskLevel]);

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="business-page-header"
      >
        <div>
          <h2 className="business-page-title">Customer Explorer</h2>
          <p className="business-page-subtitle">Search and analyze your customer base</p>
        </div>
      </motion.div>

      <div className="business-filters">
        <div className="business-search-bar">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by name, ID, email, or phone..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <select value={operator} onChange={(e) => { setOperator(e.target.value); setPage(1); }}>
          <option value="">All Operators</option>
          <option value="Airtel">Airtel</option>
          <option value="Jio">Jio</option>
          <option value="Vi">Vi</option>
          <option value="BSNL">BSNL</option>
        </select>
        <select value={riskLevel} onChange={(e) => { setRiskLevel(e.target.value); setPage(1); }}>
          <option value="">All Risk Levels</option>
          <option value="HIGH">High Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="LOW">Low Risk</option>
        </select>
      </div>

      <motion.div
        className="business-table-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
      >
        <table className="business-table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Operator</th>
              <th>Region</th>
              <th>Tenure</th>
              <th>Monthly Charges</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="business-loading">Loading customers...</td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={7} className="business-empty">No customers found</td>
              </tr>
            ) : (
              customers.map((customer) => (
                <tr key={customer.id}>
                  <td>
                    <div className="business-customer-cell">
                      <div className="business-avatar">{customer.full_name.charAt(0)}</div>
                      <div>
                        <span className="business-customer-name">{customer.full_name}</span>
                        <span className="business-customer-id">{customer.customer_id}</span>
                      </div>
                    </div>
                  </td>
                  <td>{customer.operator}</td>
                  <td>{customer.region}</td>
                  <td>{customer.tenure_months} months</td>
                  <td>${customer.monthly_charges.toFixed(2)}</td>
                  <td>
                    <span className={`business-status ${customer.churn_status.toLowerCase()}`}>
                      {customer.churn_status}
                    </span>
                  </td>
                  <td>
                    <div className="business-actions">
                      <button
                        className="business-icon-btn"
                        title="View Profile"
                        onClick={() => navigate(`/app/customers/${customer.id}`)}
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        className="business-icon-btn"
                        title="Predict Churn"
                        onClick={() => navigate(`/app/predict?customer=${customer.id}`)}
                      >
                        <BrainCircuit size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </motion.div>

      <div className="business-pagination">
        <button
          className="business-btn secondary"
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          <ChevronLeft size={16} /> Previous
        </button>
        <span>Page {page} of {Math.ceil(total / 20) || 1}</span>
        <button
          className="business-btn secondary"
          disabled={page >= Math.ceil(total / 20)}
          onClick={() => setPage(page + 1)}
        >
          Next <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
