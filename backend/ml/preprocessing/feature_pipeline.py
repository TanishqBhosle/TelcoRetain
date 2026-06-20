"""Feature pipeline for churn inference.

Transforms raw API input dictionaries into model-ready feature DataFrames
using saved label encoders from training.
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..inference.artifact_loader import ArtifactRegistry

logger = logging.getLogger(__name__)

# Categorical columns that require label encoding
CATEGORICAL_COLUMNS: List[str] = [
    "gender",
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

# Numeric columns with their default values
NUMERIC_DEFAULTS: Dict[str, float] = {
    "SeniorCitizen": 0,
    "tenure": 0,
    "MonthlyCharges": 0.0,
    "TotalCharges": 0.0,
}


class FeaturePipeline:
    """Transforms raw API input into model-ready feature vectors."""

    @staticmethod
    def transform(raw_input: Dict[str, Any]) -> pd.DataFrame:
        """Transform raw API input into a model-ready feature vector.

        Steps:
        1. Extract numeric fields with defaults for missing values
        2. Apply feature engineering (CLV, HighValueCustomer, TenureGroup)
        3. Encode categoricals using saved label encoders
        4. Order columns per feature_columns.pkl
        5. Fill any remaining NaN values

        Args:
            raw_input: Dictionary of customer feature data from the API request.

        Returns:
            A single-row pandas DataFrame with columns matching
            ArtifactRegistry.get_feature_columns() order, no NaN values.
        """
        features: Dict[str, Any] = {}

        # --- Step 1: Extract numeric fields with defaults ---
        for col, default in NUMERIC_DEFAULTS.items():
            value = raw_input.get(col)
            if value is None:
                features[col] = default
            else:
                try:
                    features[col] = float(value)
                except (ValueError, TypeError):
                    features[col] = default

        tenure = features["tenure"]
        monthly_charges = features["MonthlyCharges"]

        # --- Step 2: Feature engineering ---
        features["CLV"] = monthly_charges * tenure
        features["HighValueCustomer"] = 1 if monthly_charges > 80 else 0

        # TenureGroup: bins [0,12] → 1, (12,24] → 2, (24,48] → 3, (48,72] → 4
        features["TenureGroup"] = FeaturePipeline._compute_tenure_group(tenure)

        # --- Step 3: Encode categorical columns ---
        encoders = ArtifactRegistry.get_encoders()

        for col in CATEGORICAL_COLUMNS:
            value = raw_input.get(col)
            encoder = encoders.get(col)

            if encoder is None:
                # No encoder available for this column - use 0 as fallback
                features[col] = 0
                continue

            if value is None:
                # Missing input field - use first class in encoder as default
                if hasattr(encoder, "classes_") and len(encoder.classes_) > 0:
                    features[col] = 0  # First class encodes to 0
                else:
                    features[col] = 0
                continue

            # Attempt to encode the value
            value_str = str(value)
            try:
                # Check if the value is in the encoder's known classes
                if value_str in encoder.classes_:
                    features[col] = int(encoder.transform([value_str])[0])
                else:
                    # Unknown value - safe fallback to 0
                    features[col] = 0
            except (ValueError, TypeError):
                # Any encoding failure - fallback to 0
                features[col] = 0

        # --- Step 4: Order columns to match feature_columns.pkl ---
        feature_columns = ArtifactRegistry.get_feature_columns()

        if feature_columns:
            # Build DataFrame with exact column ordering from training
            ordered_features: Dict[str, Any] = {}
            for col in feature_columns:
                if col in features:
                    ordered_features[col] = features[col]
                else:
                    # Column expected by model but not computed - default to 0
                    ordered_features[col] = 0
            df = pd.DataFrame([ordered_features], columns=feature_columns)
        else:
            # Fallback if feature_columns not loaded
            df = pd.DataFrame([features])

        # --- Step 5: Ensure no NaN values ---
        df = df.fillna(0)

        # Ensure all values are numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    @staticmethod
    def _compute_tenure_group(tenure: float) -> int:
        """Compute TenureGroup using the same binning as training.

        Bins: [0,12] → 1, (12,24] → 2, (24,48] → 3, (48,72] → 4
        Values outside range default to 1 (for tenure <= 0) or 4 (for tenure > 72).

        Args:
            tenure: Customer tenure in months.

        Returns:
            Integer tenure group (1-4).
        """
        if tenure <= 0:
            return 1
        elif tenure <= 12:
            return 1
        elif tenure <= 24:
            return 2
        elif tenure <= 48:
            return 3
        else:
            return 4
