"""SHAP explainability module using pre-loaded model artifacts."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import shap

from ml.inference.artifact_loader import ArtifactRegistry

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """SHAP explainer using ArtifactRegistry for model access.

    Initializes once at startup based on model type from metadata.
    Uses TreeExplainer for tree-based models and LinearExplainer for
    logistic regression.
    """

    _explainer: Optional[shap.Explainer] = None

    @classmethod
    def initialize(cls) -> None:
        """Create SHAP explainer from loaded model artifact.

        Uses TreeExplainer for tree-based models (xgboost, lightgbm, random_forest)
        and LinearExplainer for logistic regression.
        """
        model = ArtifactRegistry.get_model()
        if model is None:
            logger.warning("Cannot initialize SHAPExplainer: no model loaded")
            return

        metadata = ArtifactRegistry.get_metadata()
        model_type = metadata.get("model_type", "")

        try:
            if model_type in ("xgboost", "lightgbm", "random_forest"):
                cls._explainer = shap.TreeExplainer(model)
                logger.info(
                    "Initialized SHAP TreeExplainer for model type: %s", model_type
                )
            else:
                # LinearExplainer requires background data; use a single-row
                # zeros matrix matching feature count as a minimal baseline.
                feature_columns = ArtifactRegistry.get_feature_columns()
                background = np.zeros((1, len(feature_columns)))
                cls._explainer = shap.LinearExplainer(model, background)
                logger.info(
                    "Initialized SHAP LinearExplainer for model type: %s", model_type
                )
        except Exception as e:
            logger.error("Failed to initialize SHAP explainer: %s", e)
            cls._explainer = None

    @classmethod
    def explain(cls, features_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Compute SHAP values and return top 5 drivers with direction.

        Args:
            features_df: Single-row DataFrame with model-compatible features.

        Returns:
            List of up to 5 driver dicts sorted by absolute SHAP value descending.
            Each dict has: feature_name, shap_value, feature_value, direction, rank.
            Returns empty list if SHAP computation fails.
        """
        if cls._explainer is None:
            logger.warning("SHAPExplainer not initialized, returning empty drivers")
            return []

        try:
            shap_values = cls._explainer.shap_values(features_df)

            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Multi-class output: use positive class (index 1)
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

            # Flatten to 1-D array for a single row
            if hasattr(shap_values, "ndim") and shap_values.ndim == 2:
                shap_values = shap_values[0]

            feature_columns = ArtifactRegistry.get_feature_columns()

            # Build driver list
            drivers: List[Dict[str, Any]] = []
            for idx, col in enumerate(feature_columns):
                if idx >= len(shap_values):
                    break
                shap_val = float(shap_values[idx])
                feature_val = features_df.iloc[0][col] if col in features_df.columns else 0
                direction = "increases_churn" if shap_val > 0 else "decreases_churn"

                drivers.append(
                    {
                        "feature_name": col,
                        "shap_value": shap_val,
                        "feature_value": str(feature_val),
                        "direction": direction,
                        "rank": 0,  # assigned after sorting
                    }
                )

            # Sort by absolute SHAP value descending, take top 5
            drivers.sort(key=lambda d: abs(d["shap_value"]), reverse=True)
            top_drivers = drivers[:5]

            # Assign ranks (1-based)
            for rank, driver in enumerate(top_drivers, start=1):
                driver["rank"] = rank

            return top_drivers

        except Exception as e:
            logger.error("SHAP computation failed: %s", e)
            return []
