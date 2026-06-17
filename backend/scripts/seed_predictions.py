"""Seed churn predictions for existing customers."""
import sys
sys.path.insert(0, ".")

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings

sync_url = settings.sync_database_url
engine_sync = create_engine(sync_url)

from app.models.base import Base
from app.models import *  # noqa
from app.models.customers import TelecomCustomer
from app.models.ml import ChurnPrediction, MLModel


def seed_predictions():
    with Session(engine_sync) as session:
        existing = session.execute(select(ChurnPrediction)).first()
        if existing:
            print("Predictions already seeded. Skipping.")
            return

        customers = session.execute(select(TelecomCustomer)).scalars().all()
        if not customers:
            print("No customers found. Run seed_customers.py first.")
            return

        model = session.execute(select(MLModel).where(MLModel.name == "xgboost")).scalar_one_or_none()
        if not model:
            model = session.execute(select(MLModel).limit(1)).scalar_one_or_none()
        if not model:
            print("No ML models found. Run init_db.py first.")
            return

        rng = random.Random(42)
        now = datetime.now(timezone.utc)
        predictions = []

        for cust in customers:
            if cust.churn_status:
                prob = round(rng.uniform(0.6, 0.98), 4)
                risk = "HIGH" if prob >= 0.7 else "MEDIUM"
            else:
                prob = round(rng.uniform(0.05, 0.45), 4)
                risk = "LOW" if prob < 0.3 else "MEDIUM"

            pred_date = now - timedelta(days=rng.randint(0, 90))
            pred = ChurnPrediction(
                customer_id=cust.id,
                model_id=model.id,
                churn_probability=prob,
                risk_score=int(prob * 100),
                risk_category=risk,
                prediction_date=pred_date,
            )
            predictions.append(pred)

        session.add_all(predictions)
        session.commit()
        print(f"Seeded {len(predictions)} churn predictions successfully.")


if __name__ == "__main__":
    seed_predictions()
