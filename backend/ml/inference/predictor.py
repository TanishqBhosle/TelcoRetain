"""Churn prediction using pre-loaded model artifacts."""

from typing import Tuple

import pandas as pd

from ml.inference.artifact_loader import ArtifactRegistry


class ChurnPredictor:
    """Single-model churn predictor using ArtifactRegistry."""

    @staticmethod
    def predict(features_df: pd.DataFrame) -> Tuple[float, float, str]:
        """Run churn inference on a preprocessed feature DataFrame.

        Args:
            features_df: Single-row DataFrame with model-compatible features.

        Returns:
            Tuple of (churn_probability, confidence_score, risk_category).

        Raises:
            RuntimeError: If no model is loaded in the ArtifactRegistry.
        """
        model = ArtifactRegistry.get_model()
        if model is None:
            raise RuntimeError("No ML model loaded")

        probability = float(model.predict_proba(features_df)[0][1])
        confidence = max(probability, 1.0 - probability)

        if probability >= 0.70:
            risk_category = "HIGH"
        elif probability >= 0.40:
            risk_category = "MEDIUM"
        else:
            risk_category = "LOW"

        return probability, confidence, risk_category
