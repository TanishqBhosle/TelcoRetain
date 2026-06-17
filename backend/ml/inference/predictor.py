"""Churn prediction facade over loaded model artifacts."""

from typing import Tuple

import numpy as np

from ml.inference.model_loader import ModelRegistry


class ChurnPredictor:
    @staticmethod
    def predict(features_df) -> Tuple[float, float]:
        models = ModelRegistry.get_loaded_models()
        if not models:
            raise RuntimeError("No ML models are loaded")

        # Get the expected feature columns from the features DataFrame
        expected_features = set(features_df.columns)

        probabilities = []
        for name, model in models.items():
            # Skip models trained on incompatible feature sets
            if hasattr(model, "feature_names_in_"):
                model_features = set(str(f) for f in model.feature_names_in_)
                if not model_features.issubset(expected_features) and not expected_features.issubset(model_features):
                    continue
            elif hasattr(model, "n_features_in_"):
                if model.n_features_in_ != features_df.shape[1]:
                    continue

            try:
                if hasattr(model, "predict_proba"):
                    probabilities.append(float(model.predict_proba(features_df)[0][1]))
                elif hasattr(model, "predict"):
                    probabilities.append(float(np.asarray(model.predict(features_df))[0]))
            except (ValueError, Exception):
                # Model failed prediction (feature mismatch, etc.) — skip it
                continue

        if not probabilities:
            raise RuntimeError("No compatible ML models could produce a prediction for the given features")

        probability = max(0.0, min(1.0, float(np.mean(probabilities))))
        confidence = max(probability, 1.0 - probability)
        return probability, confidence
