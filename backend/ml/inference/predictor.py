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

        probabilities = []
        for model in models.values():
            if hasattr(model, "predict_proba"):
                probabilities.append(float(model.predict_proba(features_df)[0][1]))
            elif hasattr(model, "predict"):
                probabilities.append(float(np.asarray(model.predict(features_df))[0]))

        if not probabilities:
            raise RuntimeError("Loaded artifacts do not expose predict or predict_proba")

        probability = max(0.0, min(1.0, float(np.mean(probabilities))))
        confidence = max(probability, 1.0 - probability)
        return probability, confidence
