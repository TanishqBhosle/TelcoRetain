"""Lightweight ML artifact registry.

The registry is intentionally tolerant of missing artifacts so the API can
start before training has been run. Prediction routes still enforce a loaded
registry through PredictionService.
"""

from pathlib import Path
from typing import Any, Dict

import joblib

from app.core.config import settings


class ModelRegistry:
    _models: Dict[str, Any] = {}
    _artifacts: Dict[str, Any] = {}
    _loaded = False

    @classmethod
    def initialize(cls) -> None:
        artifact_dir = Path(settings.ML_ARTIFACTS_PATH)
        cls._models = {}
        cls._artifacts = {}
        if not artifact_dir.exists():
            cls._loaded = False
            return

        for path in artifact_dir.glob("*.pkl"):
            artifact = joblib.load(path)
            cls._artifacts[path.stem] = artifact
            if hasattr(artifact, "predict") or hasattr(artifact, "predict_proba"):
                cls._models[path.stem] = artifact
        cls._loaded = bool(cls._models)

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def get_loaded_models(cls) -> Dict[str, Any]:
        return dict(cls._models)

    @classmethod
    def get(cls, name: str) -> Any:
        return cls._artifacts.get(name)

    @classmethod
    def cleanup(cls) -> None:
        cls._models = {}
        cls._artifacts = {}
        cls._loaded = False
