"""Feature assembly for churn inference."""

from typing import Any, Dict, Tuple

import pandas as pd


class FeaturePipeline:
    @staticmethod
    def assemble_features(customer: Any, latest_usage: Any = None, latest_network: Any = None, complaints_count: int = 0) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        features: Dict[str, Any] = {
            "tenure_months": getattr(customer, "tenure_months", 0) or 0,
            "arpu": float(getattr(customer, "arpu", 0) or 0),
            "complaints_count": complaints_count or 0,
            "monthly_data_gb": float(getattr(latest_usage, "data_gb", 0) or 0),
            "voice_minutes": float(getattr(latest_usage, "voice_minutes", 0) or 0),
            "call_drop_count": int(getattr(latest_usage, "call_drop_count", 0) or 0),
            "call_drop_rate": float(getattr(latest_network, "call_drop_rate", 0) or 0),
            "signal_strength": float(getattr(latest_network, "signal_strength_avg", 0) or 0),
            "network_availability": float(getattr(latest_network, "network_availability", 0) or 0),
            "latency_ms": int(getattr(latest_network, "latency_ms", 0) or 0),
        }
        return pd.DataFrame([features]), features
