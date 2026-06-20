"""Tests for the refactored prediction service."""

from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from app.schemas.predictions import PredictionResponse
from app.services.prediction_service import PredictionService


class TestPredictionService:
    """Tests for the stateless PredictionService.predict method."""

    @patch("app.services.prediction_service.RecommendationEngine")
    @patch("app.services.prediction_service.SHAPExplainer")
    @patch("app.services.prediction_service.ChurnPredictor")
    @patch("app.services.prediction_service.FeaturePipeline")
    def test_predict_returns_prediction_response(
        self, mock_pipeline, mock_predictor, mock_shap, mock_reco
    ):
        """Full pipeline produces a valid PredictionResponse."""
        mock_pipeline.transform.return_value = pd.DataFrame(
            [[0.0] * 5], columns=["a", "b", "c", "d", "e"]
        )
        mock_predictor.predict.return_value = (0.75, 0.75, "HIGH")
        mock_shap.explain.return_value = [
            {
                "feature_name": "tenure",
                "shap_value": -0.3,
                "feature_value": "2",
                "direction": "decreases_churn",
                "rank": 1,
            }
        ]
        mock_reco.generate_offers.return_value = [
            {
                "offer_type": "discount",
                "description": "20% off",
                "validity_days": 180,
                "expected_impact": "high",
                "priority": 100,
            }
        ]

        raw_input = {"tenure": 2, "MonthlyCharges": 90.0, "Contract": "Month-to-month"}
        result = PredictionService.predict(raw_input)

        assert isinstance(result, PredictionResponse)
        assert result.churn_probability == 0.75
        assert result.risk_category == "HIGH"
        assert result.confidence_score == 0.75
        assert len(result.top_churn_drivers) == 1
        assert result.top_churn_drivers[0].feature_name == "tenure"
        assert len(result.recommendations) == 1
        assert result.recommendations[0].offer_type == "discount"
        assert result.prediction_id is not None

    @patch("app.services.prediction_service.RecommendationEngine")
    @patch("app.services.prediction_service.SHAPExplainer")
    @patch("app.services.prediction_service.ChurnPredictor")
    @patch("app.services.prediction_service.FeaturePipeline")
    def test_predict_low_risk(self, mock_pipeline, mock_predictor, mock_shap, mock_reco):
        """Low risk prediction returns correct category."""
        mock_pipeline.transform.return_value = pd.DataFrame([[0.0]], columns=["a"])
        mock_predictor.predict.return_value = (0.15, 0.85, "LOW")
        mock_shap.explain.return_value = []
        mock_reco.generate_offers.return_value = []

        result = PredictionService.predict({"tenure": 60, "MonthlyCharges": 30.0})

        assert result.risk_category == "LOW"
        assert result.churn_probability == 0.15
        assert result.confidence_score == 0.85
        assert result.top_churn_drivers == []
        assert result.recommendations == []

    @patch("app.services.prediction_service.FeaturePipeline")
    def test_predict_runtime_error_when_model_not_loaded(self, mock_pipeline):
        """RuntimeError propagates when model is not loaded."""
        mock_pipeline.transform.return_value = pd.DataFrame([[0.0]], columns=["a"])

        with patch(
            "app.services.prediction_service.ChurnPredictor.predict",
            side_effect=RuntimeError("No ML model loaded"),
        ):
            with pytest.raises(RuntimeError, match="No ML model loaded"):
                PredictionService.predict({"tenure": 5})
