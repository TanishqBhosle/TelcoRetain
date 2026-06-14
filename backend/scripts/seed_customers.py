"""Seed synthetic customer data for development."""
import sys
sys.path.insert(0, ".")

import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings

sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")
engine_sync = create_engine(sync_url, connect_args={"check_same_thread": False})

from app.models.base import Base
from app.models import *  # noqa
from app.models.customers import TelecomCustomer

NAMES_MALE = [
    "Rajesh Kumar", "Amit Sharma", "Vikram Singh", "Sanjay Patel", "Rahul Verma",
    "Suresh Gupta", "Mohit Agarwal", "Deepak Mishra", "Arjun Reddy", "Kiran Deshmukh",
    "Manoj Tiwari", "Nitin Joshi", "Pankaj Saxena", "Anil Chauhan", "Ravi Prasad",
    "Vijay Mehta", "Sachin Kulkarni", "Ashok Bhatt", "Sunil Kapoor", "Gaurav Malhotra",
    "Nikhil Bose", "Rohan Das", "Aditya Nair", "Prakash Pandey", "Vinod Yadav",
    "Deepak Rao", "Tarun Chakraborty", "Arun Menon", "Rajiv Kaul", "Sanjay Bhat",
]
NAMES_FEMALE = [
    "Priya Sharma", "Neha Gupta", "Anjali Singh", "Pooja Patel", "Sunita Verma",
    "Kavita Reddy", "Meena Devi", "Rekha Joshi", "Suman Agarwal", "Geeta Pandey",
    "Asha Bose", "Usha Nair", "Lata Menon", "Seema Chauhan", "Vandana Bhat",
    "Nisha Yadav", "Pallavi Mishra", "Sapna Kulkarni", "Ritu Sinha", "Deepika Chakraborty",
    "Mamta Tiwari", "Sarojini Prasad", "Kamla Devi", "Indira Goyal", "Savita Malhotra",
    "Jyoti Saxena", "Archana Deshmukh", "Manju Kapoor", "Pushpa Jaiswal", "Bharati Rao",
]

REGIONS = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Jaipur", "Ahmedabad", "Lucknow"]
OPERATORS = ["Jio", "Airtel", "Vi (Vodafone Idea)", "BSNL", "MTNL"]
CONTRACTS = ["Month-to-month", "One year", "Two year"]
PAYMENTS = ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
PLANS = ["Basic", "Standard", "Premium", "Ultra"]


def seed_customers():
    with Session(engine_sync) as session:
        existing = session.execute(select(TelecomCustomer)).first()
        if existing:
            print("Customers already seeded. Skipping.")
            return

        customers = []
        rng = random.Random(42)
        now = datetime.now(timezone.utc)

        for i in range(200):
            is_male = rng.random() < 0.55
            name = rng.choice(NAMES_MALE if is_male else NAMES_FEMALE)
            gender = "Male" if is_male else "Female"
            age = rng.randint(18, 72)
            region = rng.choice(REGIONS)
            operator = rng.choice(OPERATORS)
            contract = rng.choice(CONTRACTS)
            tenure = rng.randint(1, 72)
            monthly = round(rng.uniform(30, 120), 2)
            total = round(monthly * tenure * rng.uniform(0.85, 1.15), 2)
            arpu = round(monthly * rng.uniform(0.7, 1.3), 2)
            churn = rng.random() < 0.27
            status = "churned" if churn else "active"
            join_date = now - timedelta(days=tenure * 30 + rng.randint(0, 30))

            cust = TelecomCustomer(
                customer_id=f"CUST-{i+1:05d}",
                full_name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone_number=f"+91{rng.randint(7000000000, 9999999999)}",
                gender=gender,
                age=age,
                region=region,
                operator=operator,
                join_date=join_date,
                contract_type=contract,
                paperless_billing=rng.random() < 0.6,
                payment_method=rng.choice(PAYMENTS),
                monthly_charges=Decimal(str(monthly)),
                total_charges=Decimal(str(total)),
                tenure_months=tenure,
                arpu=Decimal(str(arpu)),
                churn_status=churn,
                status=status,
            )
            customers.append(cust)

        session.add_all(customers)
        session.commit()
        print(f"Seeded {len(customers)} customers successfully.")


if __name__ == "__main__":
    seed_customers()
