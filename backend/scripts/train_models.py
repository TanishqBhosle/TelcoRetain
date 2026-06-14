"""Train churn models and save local artifacts.

Usage:
    python scripts/train_models.py --input data/customer_churn.csv
    python scripts/train_models.py

If no input CSV is provided, the script trains on a deterministic synthetic
dataset with the same numeric feature contract used by FeaturePipeline.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "tenure_months",
    "arpu",
    "complaints_count",
    "monthly_data_gb",
    "voice_minutes",
    "call_drop_count",
    "call_drop_rate",
    "signal_strength",
    "network_availability",
    "latency_ms",
]


def build_synthetic_dataset(rows: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    data = pd.DataFrame(
        {
            "tenure_months": rng.integers(1, 84, rows),
            "arpu": rng.normal(450, 170, rows).clip(50, 1600),
            "complaints_count": rng.poisson(1.2, rows).clip(0, 12),
            "monthly_data_gb": rng.normal(18, 8, rows).clip(0, 90),
            "voice_minutes": rng.normal(420, 180, rows).clip(0, 1800),
            "call_drop_count": rng.poisson(4, rows).clip(0, 40),
            "call_drop_rate": rng.beta(2, 18, rows).clip(0, 1),
            "signal_strength": rng.normal(-82, 13, rows).clip(-120, -45),
            "network_availability": rng.normal(96, 4, rows).clip(60, 100),
            "latency_ms": rng.normal(60, 25, rows).clip(10, 250),
        }
    )
    logits = (
        -2.2
        - 0.025 * data["tenure_months"]
        + 0.0025 * data["arpu"]
        + 0.32 * data["complaints_count"]
        + 1.8 * data["call_drop_rate"]
        + 0.012 * data["latency_ms"]
        - 0.025 * data["network_availability"]
    )
    probability = 1 / (1 + np.exp(-logits))
    data["churn"] = (rng.random(rows) < probability).astype(int)
    return data


def load_dataset(path: Path | None) -> pd.DataFrame:
    if path is None:
        return build_synthetic_dataset()
    frame = pd.read_csv(path)
    target_candidates = ["churn", "Churn", "churn_status", "Churn Status"]
    target = next((col for col in target_candidates if col in frame.columns), None)
    if target is None:
        raise ValueError(f"Input dataset must include one of: {', '.join(target_candidates)}")
    frame = frame.rename(columns={target: "churn"})
    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = 0
    if frame["churn"].dtype == object:
        frame["churn"] = frame["churn"].str.lower().isin(["yes", "true", "1", "churned"]).astype(int)
    return frame[FEATURE_COLUMNS + ["churn"]]


def candidate_models() -> Dict[str, object]:
    models: Dict[str, object] = {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=220,
            max_depth=8,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
        ),
    }
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=180,
            max_depth=4,
            learning_rate=0.06,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        )
    except Exception:
        pass
    try:
        from lightgbm import LGBMClassifier

        models["lightgbm"] = LGBMClassifier(
            n_estimators=220,
            max_depth=-1,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
        )
    except Exception:
        pass
    return models


def score_model(model: object, x_test: pd.DataFrame, y_test: pd.Series) -> Tuple[float, float]:
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_test)[:, 1]
    else:
        probabilities = predictions
    auc = roc_auc_score(y_test, probabilities)
    return float(accuracy), float(auc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="Optional CSV training dataset")
    parser.add_argument("--output-dir", type=Path, default=Path("ml/artifacts"))
    parser.add_argument("--dataset-version-id", default=None, help="Accepted for API-triggered retraining metadata")
    args = parser.parse_args()

    data = load_dataset(args.input)
    x_train, x_test, y_train, y_test = train_test_split(
        data[FEATURE_COLUMNS],
        data["churn"].astype(int),
        test_size=0.2,
        random_state=42,
        stratify=data["churn"].astype(int),
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics = {}
    trained = {}
    for name, model in candidate_models().items():
        model.fit(x_train, y_train)
        accuracy, auc = score_model(model, x_test, y_test)
        metrics[name] = {"accuracy": accuracy, "auc_score": auc}
        trained[name] = model

    ranked = sorted(metrics, key=lambda item: metrics[item]["auc_score"], reverse=True)
    selected = ranked[:2]
    for name in selected:
        joblib.dump(trained[name], args.output_dir / f"{name}.pkl")

    metadata = {
        "feature_columns": FEATURE_COLUMNS,
        "selected_models": selected,
        "metrics": metrics,
        "dataset_version_id": args.dataset_version_id,
    }
    (args.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
