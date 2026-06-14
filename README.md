# Telecom Customer Retention Intelligence Platform

FastAPI + SQLAlchemy backend and React + TypeScript frontend for churn prediction, retention recommendations, campaign tracking, analytics, model monitoring, and admin workflows.

## Backend

```powershell
cd E:\TelcoRetain\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python scripts\train_models.py
python scripts\seed_data.py
uvicorn main:app --reload
```

API docs: `http://localhost:8000/docs`

## Frontend

```powershell
cd E:\TelcoRetain\frontend
npm install
npm run dev
```

App URL: `http://localhost:5173`

Default seeded admin:

- Email: `admin@telecom-retention.com`
- Password: `Admin@1234`

## Notes

- Redis is optional for local development; the backend falls back to in-memory token blacklisting when `REDIS_URL` is unset.
- `scripts/train_models.py` can train from a CSV using `--input`, or generate deterministic synthetic training data when no CSV is provided.
- The frontend proxies `/api` and `/health` to `http://localhost:8000`.
