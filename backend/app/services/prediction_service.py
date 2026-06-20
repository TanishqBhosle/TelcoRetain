"""
Prediction Service.

Orchestrates the ML inference pipeline:
validate → FeaturePipeline.transform → ChurnPredictor.predict →
SHAPExplainer.explain → RecommendationEngine.generate_offers
"""

import logging
import uuid
from typing import Any, Dict, List

from app.schemas.predictions import (
    ChurnDriver,
    PredictionResponse,
    RetentionOffer,
)
from ml.inference.artifact_loader import ArtifactRegistry
from ml.inference.predictor import ChurnPredictor
from ml.explainability.shap_explainer import SHAPExplainer
from ml.preprocessing.feature_pipeline import FeaturePipeline
from ml.recommendations.engine import RecommendationEngine

logger = logging.getLogger(__name__)


class PredictionService:
    """Stateless prediction orchestrator using pre-loaded ML artifacts."""

    @staticmethod
    def predict(raw_input: Dict[str, Any]) -> PredictionResponse:
        """Run the full inference pipeline and return a combined response.

        Steps:
        1. Transform raw input into model-ready features
        2. Run churn inference
        3. Compute SHAP explanations
        4. Generate retention offers
        5. Assemble PredictionResponse

        Args:
            raw_input: Dictionary of customer feature data from the API request.

        Returns:
            PredictionResponse with probability, risk, drivers, and offers.

        Raises:
            RuntimeError: If model artifacts are not loaded.
        """
        # 1. Feature preprocessing
        features_df = FeaturePipeline.transform(raw_input)

        # 2. Model inference
        churn_probability, confidence_score, risk_category = ChurnPredictor.predict(features_df)

        # 3. SHAP explainability
        shap_drivers = SHAPExplainer.explain(features_df)

        # 4. Recommendation generation
        customer_features: Dict[str, Any] = {
            "Contract": raw_input.get("Contract", ""),
            "MonthlyCharges": raw_input.get("MonthlyCharges", 0),
            "tenure": raw_input.get("tenure", 0),
        }
        offers = RecommendationEngine.generate_offers(
            churn_probability=churn_probability,
            risk_category=risk_category,
            customer_features=customer_features,
        )

        # 5. Assemble response
        top_churn_drivers = [
            ChurnDriver(
                feature_name=d["feature_name"],
                shap_value=d["shap_value"],
                feature_value=d["feature_value"],
                direction=d["direction"],
                rank=d["rank"],
            )
            for d in shap_drivers
        ]

        recommendations = [
            RetentionOffer(
                offer_type=o["offer_type"],
                description=o["description"],
                validity_days=o["validity_days"],
                expected_impact=o["expected_impact"],
                priority=o["priority"],
            )
            for o in offers
        ]

        return PredictionResponse(
            churn_probability=churn_probability,
            risk_category=risk_category,
            confidence_score=confidence_score,
            top_churn_drivers=top_churn_drivers,
            recommendations=recommendations,
            prediction_id=uuid.uuid4(),
        )



def _run_batch_prediction(customer_ids: List[str]) -> None:
    """Run batch predictions for a list of customer IDs.

    This is a placeholder used by the scheduler for background batch jobs.
    It iterates through customer IDs and logs predictions.
    In production, this would load customer data from DB and store results.
    """
    logger.info(f"Starting batch prediction for {len(customer_ids)} customers")
    for cid in customer_ids:
        logger.info(f"Batch prediction queued for customer: {cid}")
    logger.info("Batch prediction job complete")
