"""Feature assembly for churn inference."""

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


TELCO_FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "CLV",
    "HighValueCustomer",
    "TenureGroup",
]

CONTRACT_MAP = {"month-to-month": 0, "one year": 1, "two year": 2}
PAYMENT_MAP = {
    "bank transfer (automatic)": 0,
    "credit card (automatic)": 1,
    "electronic check": 2,
    "mailed check": 3,
}
INTERNET_MAP = {"dsl": 0, "fiber optic": 1, "no": 2}
YES_NO_MAP = {"no": 0, "yes": 1}


def _map_value(value: Any, mapping: Dict, default: int = 0) -> int:
    if value is None:
        return default
    return mapping.get(str(value).lower(), default)


def _map_yes_no(value: Any) -> int:
    if value is None:
        return 0
    v = str(value).lower()
    return 1 if v in ("yes", "true", "1") else 0


class FeaturePipeline:
    @staticmethod
    def assemble_features(
        customer: Any,
        latest_usage: Any = None,
        latest_network: Any = None,
        complaints_count: int = 0,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        tenure = int(getattr(customer, "tenure_months", 0) or 0)
        monthly = float(getattr(customer, "monthly_charges", 0) or 0)
        total = float(getattr(customer, "total_charges", 0) or 0)

        features: Dict[str, Any] = {
            "gender": _map_yes_no(getattr(customer, "gender", None)),
            "SeniorCitizen": int(getattr(customer, "age", 0) or 0) >= 65,
            "Partner": 0,
            "Dependents": 0,
            "tenure": tenure,
            "PhoneService": 1,
            "MultipleLines": 0,
            "InternetService": _map_value(
                getattr(customer, "internet_service", None), INTERNET_MAP, 1
            ),
            "OnlineSecurity": 0,
            "OnlineBackup": 0,
            "DeviceProtection": 0,
            "TechSupport": 0,
            "StreamingTV": 0,
            "StreamingMovies": 0,
            "Contract": _map_value(
                getattr(customer, "contract_type", None), CONTRACT_MAP, 0
            ),
            "PaperlessBilling": int(getattr(customer, "paperless_billing", False) or False),
            "PaymentMethod": _map_value(
                getattr(customer, "payment_method", None), PAYMENT_MAP, 2
            ),
            "MonthlyCharges": monthly,
            "TotalCharges": total,
            "CLV": monthly * tenure,
            "HighValueCustomer": int(monthly > 80),
            "TenureGroup": min(max(tenure // 12, 1), 4),
        }

        return pd.DataFrame([features]), features
