"""
Explanation & SHAP Explainer Service.
"""

import uuid
from typing import List, Optional

from app.exceptions.custom import NotFoundError
from app.repositories.prediction_repo import PredictionRepository
from app.schemas.explanations import ChurnExplanationResponse, FeatureExplanationResponse


class ExplanationService:
    """Translates model-driven SHAP outputs into business-friendly retention triggers."""

    def __init__(self, prediction_repo: PredictionRepository) -> None:
        self.prediction_repo = prediction_repo

    async def get_prediction_explanation(self, prediction_uuid: uuid.UUID) -> ChurnExplanationResponse:
        """Retrieve SHAP explanation logs and map top drivers to business reason codes."""
        prediction = await self.prediction_repo.get_by_id(prediction_uuid)
        if not prediction:
            raise NotFoundError(f"Prediction with ID '{prediction_uuid}' not found")

        # Sort explanations by absolute SHAP value (descending importance)
        sorted_exps = sorted(prediction.explanations, key=lambda x: abs(x.shap_value), reverse=True)

        features = []
        top_drivers = []
        reasons = []

        for rank, exp in enumerate(sorted_exps, start=1):
            feat_resp = FeatureExplanationResponse(
                id=exp.id,
                feature_name=exp.feature_name,
                shap_value=float(exp.shap_value),
                feature_value=exp.feature_value,
                feature_importance_rank=rank,
            )
            features.append(feat_resp)
            if rank <= 5:
                top_drivers.append(feat_resp)
                # Map positive SHAP contributors (increasing churn probability) to reasons
                if exp.shap_value > 0.01:
                    reason_text = self._map_to_business_reason(exp.feature_name, exp.feature_value)
                    if reason_text and reason_text not in reasons:
                        reasons.append(reason_text)

        # Fallback reason
        if not reasons:
            reasons.append("Customer profiles indicate high monthly charges compared to average tenure values.")

        return ChurnExplanationResponse(
            prediction_id=prediction.id,
            model_id=prediction.model_id,
            explanation_date=prediction.prediction_date,
            features=features,
            top_drivers=top_drivers,
            reasons=reasons,
        )

    def _map_to_business_reason(self, feature: str, val: str) -> Optional[str]:
        """Maps model technical columns to human-readable explanations."""
        feat_lower = feature.lower()
        
        # 1. Billing
        if "monthly_charges" in feat_lower or "monthlycharges" in feat_lower:
            return f"High monthly billing charges (${float(val):.2f}) relative to peer rates."
        if "total_charges" in feat_lower or "totalcharges" in feat_lower:
            return "Elevated total charges accrued over active lifecycle months."
            
        # 2. Support tickets & complaints
        if "support" in feat_lower or "complaint" in feat_lower or "ticket" in feat_lower:
            return f"Frequent support complaints filed recently (Count: {val})."
            
        # 3. Call Quality
        if "call_drop" in feat_lower or "calldrop" in feat_lower:
            return f"Experienced high volume of daily call drop events (Count: {val})."
            
        # 4. Tenure & Contract
        if "tenure" in feat_lower:
            return f"Relatively low active service duration (Tenure: {val} months)."
        if "contract" in feat_lower:
            return f"Currently enrolled in a flexible {val} plan type."
            
        # 5. Usage Drops
        if "voice_minutes" in feat_lower or "voice_mins" in feat_lower:
            return "Declining usage volume for voice calls over the last 30 days."
        if "data_gb" in feat_lower:
            return "Significant reduction in monthly cellular data utilization."
            
        # 6. Network logs
        if "latency" in feat_lower:
            return f"Experiencing high transmission latency (average {val} ms)."
        if "signal_strength" in feat_lower or "signal" in feat_lower:
            return f"Poor regional signal coverage experienced (strength: {val})."

        return None
