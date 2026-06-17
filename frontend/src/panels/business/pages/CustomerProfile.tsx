import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Users, Phone, Mail, MapPin, Calendar, CreditCard, Activity, AlertTriangle, CheckCircle } from "lucide-react";
import { api, unwrap } from "../../../lib/api";

type CustomerDetail = {
  id: string;
  customer_id: string;
  full_name: string;
  email: string;
  phone_number: string;
  gender: string;
  age: number;
  region: string;
  operator: string;
  join_date: string;
  contract_type: string;
  monthly_charges: string;
  total_charges: string;
  tenure_months: number;
  arpu: string;
  status: string;
};

export function CustomerProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<CustomerDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      unwrap<CustomerDetail>(api.get(`/customers/${id}`))
        .then(setCustomer)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <div className="business-page">
        <div className="business-loading">Loading customer profile...</div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="business-page">
        <div className="business-empty">Customer not found</div>
      </div>
    );
  }

  return (
    <div className="business-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="business-page-header"
      >
        <button className="business-back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} /> Back
        </button>
        <div>
          <h2 className="business-page-title">{customer.full_name}</h2>
          <p className="business-page-subtitle">Customer ID: {customer.customer_id}</p>
        </div>
      </motion.div>

      <div className="business-profile-grid">
        <motion.div
          className="business-profile-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <h3>Personal Information</h3>
          <div className="business-profile-info">
            <div className="business-info-item">
              <Mail size={16} />
              <span>{customer.email}</span>
            </div>
            <div className="business-info-item">
              <Phone size={16} />
              <span>{customer.phone_number}</span>
            </div>
            <div className="business-info-item">
              <Users size={16} />
              <span>{customer.gender}, {customer.age} years</span>
            </div>
            <div className="business-info-item">
              <MapPin size={16} />
              <span>{customer.region}</span>
            </div>
            <div className="business-info-item">
              <Calendar size={16} />
              <span>Joined: {new Date(customer.join_date).toLocaleDateString()}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="business-profile-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <h3>Account Details</h3>
          <div className="business-profile-info">
            <div className="business-info-item">
              <CreditCard size={16} />
              <span>Operator: {customer.operator}</span>
            </div>
            <div className="business-info-item">
              <Activity size={16} />
              <span>Contract: {customer.contract_type}</span>
            </div>
            <div className="business-info-item">
              <Calendar size={16} />
              <span>Tenure: {customer.tenure_months} months</span>
            </div>
            <div className="business-info-item">
              <CreditCard size={16} />
              <span>Monthly: ₹{Number(customer.monthly_charges).toFixed(2)}</span>
            </div>
            <div className="business-info-item">
              <CreditCard size={16} />
              <span>Total: ₹{Number(customer.total_charges).toFixed(2)}</span>
            </div>
            <div className="business-info-item">
              <Activity size={16} />
              <span>ARPU: ₹{Number(customer.arpu).toFixed(2)}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="business-profile-card status-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <h3>Churn Status</h3>
          <div className="business-status-display">
            {customer.status === "churned" ? (
              <AlertTriangle size={48} className="text-danger" />
            ) : (
              <CheckCircle size={48} className="text-success" />
            )}
            <span className={`business-status-large ${customer.status.toLowerCase()}`}>
              {customer.status.charAt(0).toUpperCase() + customer.status.slice(1)}
            </span>
          </div>
        </motion.div>
      </div>

      <motion.div
        className="business-actions-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <h3>Actions</h3>
        <div className="business-actions-grid">
          <button
            className="business-action-card"
            onClick={() => navigate(`/app/predict?customer=${customer.id}`)}
          >
            <Activity size={24} />
            <span>Run Prediction</span>
          </button>
          <button className="business-action-card">
            <AlertTriangle size={24} />
            <span>View Recommendations</span>
          </button>
        </div>
      </motion.div>
    </div>
  );
}
