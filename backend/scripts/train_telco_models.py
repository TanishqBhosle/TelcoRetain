"""Train churn models on IBM Telco Customer Churn Dataset.

Usage:
    python scripts/train_telco_models.py
    python scripts/train_telco_models.py --input data/WA_Fn-UseC_-Telco-Customer-Churn.csv

This script implements the full ML pipeline from the Colab notebook:
1. Data cleaning & preprocessing
2. Feature engineering
3. Model training (LR, RF, XGBoost, LightGBM)
4. Evaluation & artifact saving
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except ImportError:
    LGBMClassifier = None


TELCO_FEATURE_COLUMNS = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "CLV",
    "HighValueCustomer",
    "TenureGroup",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
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
]


def load_telco_dataset(path: Path) -> pd.DataFrame:
    """Load and preprocess the IBM Telco Customer Churn Dataset."""
    df = pd.read_csv(path)

    df.drop("customerID", axis=1, inplace=True, errors="ignore")

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

    df["Churn"] = df["Churn"].map({"No": 0, "Yes": 1})

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features matching the Colab notebook."""
    df["CLV"] = df["MonthlyCharges"] * df["tenure"]
    df["HighValueCustomer"] = np.where(df["MonthlyCharges"] > 80, 1, 0)
    df["TenureGroup"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=[1, 2, 3, 4],
    )
    df["TenureGroup"] = df["TenureGroup"].astype(float).fillna(1).astype(int)
    return df


def encode_categoricals(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Label-encode every object/string column. Returns (df, encoders)."""
    encoders: Dict[str, LabelEncoder] = {}
    categorical_columns = df.select_dtypes(include=["object", "string"]).columns
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return df, encoders


def candidate_models() -> Dict[str, object]:
    models: Dict[str, object] = {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        ),
    }
    if XGBClassifier is not None:
        models["xgboost"] = XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            enable_categorical=True,
            eval_metric="logloss",
        )
    if LGBMClassifier is not None:
        models["lightgbm"] = LGBMClassifier(
            n_estimators=300,
            learning_rate=0.05,
            random_state=42,
        )
    return models


def evaluate_model(
    name: str, y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray
) -> Dict[str, float]:
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred), 4),
        "recall": round(recall_score(y_true, y_pred), 4),
        "f1_score": round(f1_score(y_true, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_true, y_prob), 4),
    }
    print(f"\n{'=' * 50}")
    print(f"  {name}")
    print(f"{'=' * 50}")
    for k, v in metrics.items():
        print(f"  {k:>10}: {v}")
    print(f"\n{classification_report(y_true, y_pred)}")
    return metrics


def generate_offer(probability: float) -> str:
    if probability > 0.85:
        return "20% Recharge Discount"
    elif probability > 0.70:
        return "5GB Free Data Booster"
    elif probability > 0.50:
        return "OTT Subscription Offer"
    else:
        return "Loyalty Reward"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train telco churn models")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/WA_Fn-UseC_-Telco-Customer-Churn.csv"),
        help="Path to the IBM Telco Customer Churn CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("ml/artifacts"),
        help="Directory to save model artifacts",
    )
    parser.add_argument(
        "--dataset-version-id",
        default=None,
        help="Accepted for API-triggered retraining metadata",
    )
    args = parser.parse_args()

    print("Loading dataset...")
    df = load_telco_dataset(args.input)
    print(f"  Shape: {df.shape}")

    print("Engineering features...")
    df = engineer_features(df)

    print("Encoding categorical features...")
    df, encoders = encode_categoricals(df)

    df = df.dropna()

    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    feature_columns = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"  Train: {X_train.shape[0]} rows | Test: {X_test.shape[0]} rows")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_metrics: Dict[str, Dict] = {}
    trained_models: Dict[str, object] = {}

    print("\nTraining models...")
    for name, model in candidate_models().items():
        print(f"\n  Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = y_pred.astype(float)
        all_metrics[name] = evaluate_model(name, y_test, y_pred, y_prob)
        trained_models[name] = model

    ranked = sorted(all_metrics, key=lambda m: all_metrics[m]["roc_auc"], reverse=True)
    selected = ranked[:2]

    print(f"\nSelected models (by ROC-AUC): {selected}")
    for name in selected:
        joblib.dump(trained_models[name], args.output_dir / f"{name}.pkl")
        print(f"  Saved {name}.pkl")

    joblib.dump(feature_columns, args.output_dir / "feature_columns.pkl")
    joblib.dump(encoders, args.output_dir / "telco_encoders.pkl")

    metadata = {
        "dataset": "IBM Telco Customer Churn",
        "feature_columns": feature_columns,
        "selected_models": selected,
        "metrics": all_metrics,
        "dataset_version_id": args.dataset_version_id,
        "offer_engine": {
            "thresholds": [0.85, 0.70, 0.50],
            "offers": [
                "20% Recharge Discount",
                "5GB Free Data Booster",
                "OTT Subscription Offer",
                "Loyalty Reward",
            ],
        },
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"\nMetadata saved to {args.output_dir / 'metadata.json'}")
    print("\nTraining complete.")


if __name__ == "__main__":
    main()
