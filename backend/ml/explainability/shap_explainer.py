"""Async SHAP persistence hook with real TreeExplainer implementation."""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import shap

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.ml import ChurnExplanation
from app.repositories.prediction_repo import PredictionRepository
from sqlalchemy import select


class SHAPExplainer:
    """SHAP explainer using TreeExplainer for XGBoost/LightGBM models."""
    
    def __init__(self):
        self._explainer = None
        self._feature_columns = None
        self._model = None
    
    def load_model(self, model_id: uuid.UUID) -> bool:
        """Load model and create SHAP explainer."""
        from app.repositories.model_repo import ModelRepository
        
        async def _load():
            async with AsyncSessionLocal() as db:
                model_repo = ModelRepository(db)
                model = await model_repo.get_by_id(model_id)
                if not model:
                    return False
                
                # Load the model artifact
                model_path = Path(model.model_path)
                if not model_path.exists():
                    return False
                
                self._model = joblib.load(model_path)
                self._feature_columns = model.feature_columns
                
                # Create TreeExplainer for tree-based models
                try:
                    self._explainer = shap.TreeExplainer(self._model)
                    return True
                except Exception:
                    # Fallback for non-tree models
                    try:
                        self._explainer = shap.Explainer(self._model)
                        return True
                    except Exception:
                        return False
        
        import asyncio
        return asyncio.run(_load())
    
    def explain(self, features_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compute SHAP values for a single prediction."""
        if self._explainer is None or self._feature_columns is None:
            return []
        
        # Create feature vector in correct order
        feature_vector = np.array([[features_dict.get(col, 0) for col in self._feature_columns]])
        feature_df = pd.DataFrame(feature_vector, columns=self._feature_columns)
        
        try:
            # Compute SHAP values
            shap_values = self._explainer.shap_values(feature_df)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Multi-class: use positive class (index 1)
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # For single output, shap_values shape is (1, n_features)
            if shap_values.ndim == 2:
                shap_values = shap_values[0]
            
            # Build explanation list
            explanations = []
            for idx, col in enumerate(self._feature_columns):
                shap_val = float(shap_values[idx]) if idx < len(shap_values) else 0.0
                feature_val = features_dict.get(col, "N/A")
                
                explanations.append({
                    "feature_name": col,
                    "shap_value": shap_val,
                    "feature_value": str(feature_val),
                    "feature_importance_rank": 0  # Will be set after sorting
                })
            
            # Sort by absolute SHAP value and assign ranks
            explanations.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
            for rank, exp in enumerate(explanations, 1):
                exp["feature_importance_rank"] = rank
            
            return explanations
            
        except Exception as e:
            print(f"SHAP computation error: {e}")
            return []


_explainer_cache: Dict[uuid.UUID, SHAPExplainer] = {}


def get_explainer(model_id: uuid.UUID) -> Optional[SHAPExplainer]:
    """Get or create SHAP explainer for a model."""
    if model_id not in _explainer_cache:
        explainer = SHAPExplainer()
        if explainer.load_model(model_id):
            _explainer_cache[model_id] = explainer
            return explainer
        return None
    return _explainer_cache[model_id]


async def explain_and_save_async(prediction_id: uuid.UUID, model_id: uuid.UUID, features_dict: Dict[str, Any]) -> None:
    """Compute SHAP explanations and persist to database."""
    explainer = get_explainer(model_id)
    if not explainer:
        return
    
    explanations_data = explainer.explain(features_dict)
    if not explanations_data:
        return
    
    # Persist to database
    async with AsyncSessionLocal() as db:
        pred_repo = PredictionRepository(db)
        explanations = []
        for exp_data in explanations_data:
            exp = ChurnExplanation(
                prediction_id=prediction_id,
                model_id=model_id,
                feature_name=exp_data["feature_name"],
                shap_value=exp_data["shap_value"],
                feature_value=exp_data["feature_value"],
                feature_importance_rank=exp_data["feature_importance_rank"],
            )
            explanations.append(exp)
        
        await pred_repo.save_explanations(explanations)


async def get_prediction_explanation(prediction_id: uuid.UUID) -> Dict[str, Any]:
    """Retrieve and format SHAP explanation for a prediction."""
    async with AsyncSessionLocal() as db:
        pred_repo = PredictionRepository(db)
        explanations = await pred_repo.get_explanations(prediction_id)
        
        if not explanations:
            return {
                "features": [],
                "shap_values": [],
                "top_drivers": [],
                "reasons": []
            }
        
        features = [e.feature_name for e in explanations]
        shap_values = [float(e.shap_value) for e in explanations]
        feature_values = [e.feature_value for e in explanations]
        ranks = [e.feature_importance_rank for e in explanations]
        
        # Top drivers (highest absolute SHAP)
        top_drivers = [
            {
                "feature": e.feature_name,
                "shap_value": float(e.shap_value),
                "feature_value": e.feature_value,
                "direction": "increases_churn" if e.shap_value > 0 else "decreases_churn",
                "rank": e.feature_importance_rank
            }
            for e in explanations[:5]
        ]
        
        # Business-friendly reasons
        reasons = _generate_reasons(top_drivers)
        
        return {
            "features": features,
            "shap_values": shap_values,
            "feature_values": feature_values,
            "ranks": ranks,
            "top_drivers": top_drivers,
            "reasons": reasons
        }


def _generate_reasons(top_drivers: List[Dict[str, Any]]) -> List[str]:
    """Convert SHAP drivers to business-friendly churn reasons."""
    reason_map = {
        "complaints_count": "High number of support complaints",
        "call_drop_rate": "Frequent call drops experienced",
        "call_drop_count": "Multiple call drops in recent period",
        "latency_ms": "High network latency",
        "signal_strength": "Weak signal strength",
        "network_availability": "Poor network availability",
        "tenure_months": "Short tenure (new customer)",
        "arpu": "Low average revenue per user",
        "monthly_data_gb": "Low data usage indicating disengagement",
        "voice_minutes": "Declining voice usage",
        "recharge_frequency": "Irregular recharge pattern",
    }
    
    reasons = []
    for driver in top_drivers:
        feature = driver["feature"]
        direction = driver["direction"]
        base_reason = reason_map.get(feature, f"Factor: {feature}")
        
        if direction == "increases_churn":
            reasons.append(base_reason)
        else:
            reasons.append(f"Positive: {base_reason.lower()}")
    
    return reasons
