<div align="center">

# Telco Retain

### Telecom Customer Retention Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An AI-powered platform that predicts customer churn, explains why subscribers might leave, and recommends personalized retention offers — built for telecom operators.

[**Live Demo**](#) · [**API Docs**](#api-documentation) · [**Report Bug**](https://github.com/TanishqBhosle/TelcoRetain/issues)

</div>

---

## Overview

Telco Retain combines machine learning predictions with actionable insights to help telecom retention teams reduce customer attrition. The platform processes customer behavior data (usage patterns, recharge history, network quality, support tickets) through ensemble ML models and generates explainable churn predictions with SHAP-based feature attribution.

### Key Capabilities

| Capability | Description |
|:--|:--|
| **Churn Prediction** | Ensemble models (XGBoost + Logistic Regression) predict churn risk with 83.9% AUC |
| **SHAP Explainability** | Every prediction includes feature-level explanations and business-friendly reason codes |
| **Retention Offers** | Rule-based engine generates personalized offers (discounts, data bonuses, loyalty rewards) |
| **Campaign Management** | Create, target, and track retention campaigns with conversion analytics |
| **Real-Time Dashboard** | KPIs, churn trends, revenue at risk, regional analysis, operator exposure |
| **Customer 360°** | Unified profiles with usage, recharge history, support tickets, and activity timeline |
| **Model Monitoring** | Track model performance, retrain models, and manage the ML lifecycle |
| **Enterprise Security** | JWT auth, RBAC (6 roles), rate limiting, audit logging, account lockout |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React + TypeScript (Vite)                    │
│   22 screens · Tailwind CSS · Recharts · Framer Motion          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────────┐   │
│  │   Auth   │ │Customers │ │ Predictions│ │  Recommendations │   │
│  │  Module  │ │  Module  │ │   Module   │ │     Module       │   │
│  └─────────┘ └──────────┘ └────────────┘ └──────────────────┘   │
│  ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────────┐   │
│  │Campaigns │ │Dashboard │ │   Models   │ │     Admin        │   │
│  │  Module  │ │  Module  │ │   Module   │ │     Module       │   │
│  └─────────┘ └──────────┘ └────────────┘ └──────────────────┘   │
│                                                                  │
│  12 Service Classes · 11 Repository Classes · Pydantic v2       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌────────▼────────┐ ┌─────────▼─────────┐ ┌────────▼────────┐
│  Neon PostgreSQL │ │  Redis (optional) │ │   ML Artifacts  │
│   22 tables      │ │  Cache + Blacklist│ │   .pkl files    │
└─────────────────┘ └───────────────────┘ └─────────────────┘
```

---

## Model Performance

Trained on the [IBM Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) dataset:

| Model | Accuracy | Precision | Recall | F1 | AUC-ROC |
|:--|:--:|:--:|:--:|:--:|:--:|
| **Logistic Regression** | 74.2% | 50.9% | 79.4% | 0.620 | **0.839** |
| XGBoost | 79.4% | 63.9% | 51.1% | 0.568 | 0.832 |
| LightGBM | 79.0% | 62.5% | 52.1% | 0.569 | 0.830 |
| Random Forest | 77.4% | 56.5% | 63.9% | 0.600 | 0.823 |

**Selected models:** Logistic Regression + XGBoost (highest AUC)

---

## Tech Stack

### Backend

| Component | Technology |
|:--|:--|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | Neon PostgreSQL (asyncpg) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Rate Limiting | SlowAPI |
| ML Models | XGBoost, LightGBM, scikit-learn |
| Explainability | SHAP (TreeExplainer) |
| Scheduling | APScheduler |
| Logging | structlog + Loguru |
| Caching | Redis (optional, in-memory fallback) |

### Frontend

| Component | Technology |
|:--|:--|
| Framework | React 18 + TypeScript 5.7 |
| Build Tool | Vite 6 |
| Routing | React Router v6 |
| State | Zustand |
| Charts | Recharts |
| Animations | Framer Motion |
| HTTP Client | Axios |
| Icons | Lucide React |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon account)
- Redis (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/TanishqBhosle/TelcoRetain.git
cd TelcoRetain
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, etc.

# Run database migrations
alembic upgrade head

# Train ML models (generates synthetic data if no CSV provided)
python scripts/train_models.py
# Or train on IBM Telco dataset:
python scripts/train_models.py --input data/WA_Fn-UseC_-Telco-Customer-Churn.csv

# Seed roles, permissions, and admin user
python scripts/seed_data.py

# Start the server
uvicorn main:app --reload
```

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Application: [http://localhost:5173](http://localhost:5173)

### 4. Default Credentials

| Field | Value |
|:--|:--|
| Email | `admin@telecom-retention.com` |
| Password | `Admin@1234` |

---

## Environment Variables

| Variable | Default | Description |
|:--|:--|:--|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `SECRET_KEY` | — | JWT signing secret (generate a strong one) |
| `REDIS_URL` | — | Redis URL (optional, falls back to in-memory) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins |
| `ML_ARTIFACTS_PATH` | `ml/artifacts` | Path to trained model files |
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `production` | Environment name |

See `backend/.env.example` for the full list.

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|:--|:--|:--|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Blacklist token |
| GET | `/api/v1/auth/me` | Get current user |

### Customers
| Method | Endpoint | Description |
|:--|:--|:--|
| GET | `/api/v1/customers` | List (paginated, filterable) |
| POST | `/api/v1/customers` | Create customer |
| GET | `/api/v1/customers/{id}` | Customer detail |
| GET | `/api/v1/customers/{id}/timeline` | Activity timeline |
| GET | `/api/v1/customers/{id}/usage` | Usage history |
| GET | `/api/v1/customers/{id}/complaints` | Support tickets |
| GET | `/api/v1/customers/{id}/recharge-history` | Recharge records |

### Predictions
| Method | Endpoint | Description |
|:--|:--|:--|
| POST | `/api/v1/predictions/predict` | Single churn prediction |
| POST | `/api/v1/predictions/bulk` | Batch predictions |
| GET | `/api/v1/predictions/history` | Prediction history |
| GET | `/api/v1/predictions/{id}` | Prediction detail |
| GET | `/api/v1/predictions/{id}/explanation` | SHAP explanation |
| GET | `/api/v1/predictions/{id}/reasons` | Business reason codes |

### Recommendations
| Method | Endpoint | Description |
|:--|:--|:--|
| POST | `/api/v1/recommendations/generate` | Generate retention offers |
| GET | `/api/v1/recommendations/{id}` | Offer detail |

### Campaigns
| Method | Endpoint | Description |
|:--|:--|:--|
| POST | `/api/v1/campaigns` | Create campaign |
| GET | `/api/v1/campaigns` | List campaigns |
| GET | `/api/v1/campaigns/{id}` | Campaign detail |
| GET | `/api/v1/campaigns/{id}/analytics` | Campaign analytics |

### Dashboard & Analytics
| Method | Endpoint | Description |
|:--|:--|:--|
| GET | `/api/v1/dashboard/kpis` | Key performance indicators |
| GET | `/api/v1/dashboard/churn-trends` | Churn trend data |
| GET | `/api/v1/dashboard/revenue-risk` | Revenue at risk |
| GET | `/api/v1/dashboard/regional-analysis` | Regional breakdown |
| GET | `/api/v1/dashboard/operator-analysis` | Operator exposure |

### Admin
| Method | Endpoint | Description |
|:--|:--|:--|
| GET | `/api/v1/admin/system-health` | System health check |
| GET | `/api/v1/admin/users` | List users |
| PUT | `/api/v1/admin/users/{id}` | Update user |
| DELETE | `/api/v1/admin/users/{id}` | Delete user |
| GET | `/api/v1/admin/audit-logs` | Audit trail |

### Health Checks
| Method | Endpoint | Description |
|:--|:--|:--|
| GET | `/health` | Application health |
| GET | `/health/db` | Database connectivity |
| GET | `/health/ml` | ML model status |

---

## Frontend Screens

| Screen | Route | Auth | Description |
|:--|:--|:--:|:--|
| Landing Page | `/` | No | Marketing page with features and CTA |
| About | `/about` | No | Platform information and tech stack |
| Pricing | `/pricing` | No | Three-tier pricing plans |
| Contact | `/contact` | No | Contact form and information |
| Sign In | `/signin` | No | User login |
| Sign Up | `/signup` | No | User registration |
| Dashboard | `/dashboard` | Yes | KPIs and churn trend charts |
| Customer Explorer | `/customers` | Yes | Searchable customer table |
| Customer Detail | `/customers/:id` | Yes | Full customer profile with tabs |
| Churn Prediction | `/predict` | Yes | Single and bulk prediction |
| Prediction Detail | `/predict/:id` | Yes | SHAP explanations and reasons |
| Retention Offers | `/recommendations` | Yes | Generate personalized offers |
| Campaigns | `/campaigns` | Yes | Campaign list and creation |
| Campaign Detail | `/campaigns/:id` | Yes | Campaign analytics and targets |
| Analytics | `/analytics` | Yes | Regional and operator charts |
| Model Monitoring | `/models` | Yes | ML model registry and retraining |
| Admin | `/admin` | Yes | System health and user management |
| Audit Logs | `/admin/audit-logs` | Yes | User actions and API logs |

---

## Database Schema

22 tables across 7 domains:

| Domain | Tables |
|:--|:--|
| **User & Access** | `roles`, `permissions`, `users`, `role_permissions` |
| **Customer Master** | `telecom_customers` |
| **Behavior & Usage** | `recharge_history`, `usage_metrics`, `network_quality`, `customer_support`, `plan_change_history` |
| **ML & Prediction** | `ml_models`, `churn_predictions`, `churn_explanations` |
| **Recommendation** | `retention_recommendations` |
| **Campaign** | `campaigns`, `campaign_targets`, `campaign_results` |
| **Data Management** | `datasets`, `dataset_versions` |
| **Audit & Monitoring** | `audit_logs`, `api_logs`, `model_performance_logs` |

---

## Project Structure

```
TelcoRetain/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (11 routers)
│   │   ├── core/            # Config, database, security, logging
│   │   ├── dependencies/    # FastAPI dependencies
│   │   ├── exceptions/      # Custom exceptions + handlers
│   │   ├── middleware/       # Auth, rate limit, audit
│   │   ├── models/          # SQLAlchemy ORM (22 tables)
│   │   ├── repositories/    # Data access layer (11 repos)
│   │   ├── schemas/         # Pydantic request/response (13 files)
│   │   ├── routes/          # Router assembly
│   │   └── services/        # Business logic (12 services)
│   ├── ml/
│   │   ├── artifacts/       # Trained model files (.pkl)
│   │   ├── explainability/  # SHAP explainer
│   │   ├── inference/       # Model loader + predictor
│   │   ├── preprocessing/   # Feature pipeline
│   │   └── recommendations/ # Offer engine
│   ├── scripts/             # Training, seeding, init
│   ├── tests/               # 15 test files
│   ├── migrations/          # Alembic migrations
│   ├── main.py              # Application entry point
│   └── requirements.txt     # 65 Python packages
├── frontend/
│   ├── src/
│   │   ├── components/      # Shared UI + animations
│   │   ├── lib/             # API client (Axios)
│   │   ├── pages/           # 22 page components
│   │   └── state/           # Zustand stores
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov=ml --cov-report=html
```

---

## Deployment

### Backend (Render / Railway)

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Configure environment variables (DATABASE_URL, SECRET_KEY, etc.)

### Frontend (Vercel / Netlify)

1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Configure rewrites: `/* → /index.html` (SPA routing)

### Docker

```bash
# Backend
docker build -t telco-retain-backend ./backend
docker run -p 8000:8000 telco-retain-backend

# Frontend
docker build -t telco-retain-frontend ./frontend
docker run -p 5173:80 telco-retain-frontend
```

---

## Security Features

- JWT authentication with access + refresh tokens
- bcrypt password hashing
- Account lockout after 5 failed attempts (15-minute window)
- Email verification flow
- Password reset flow
- Redis-based token blacklisting on logout
- Rate limiting (10/min auth, 60/min predictions, 120/min other)
- CORS with explicit origin allowlist
- Audit logging for all authenticated actions
- RBAC with 6 predefined roles

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with care for telecom retention teams**

[⬆ Back to Top](#telco-retain)

</div>
