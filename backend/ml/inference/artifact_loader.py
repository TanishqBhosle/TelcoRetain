"""
Singleton registry for pre-trained ML artifacts.

Loads churn_model.pkl, label_encoders.pkl, feature_columns.pkl, and
model_metadata.json from the configured models directory at startup.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import joblib
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class ArtifactRegistry:
    """Singleton registry for pre-trained ML artifacts."""

    _model: Any = None
    _encoders: Dict[str, LabelEncoder] = {}
    _feature_columns: List[str] = []
    _metadata: Dict[str, Any] = {}
    _loaded: bool = False

    @classmethod
    def initialize(cls, models_dir: Path) -> None:
        """Load all artifacts from models_dir.

        Tolerant of missing or corrupt files — logs warnings and sets
        _loaded = False rather than crashing.

        Args:
            models_dir: Path to the directory containing the model artifacts.
        """
        models_dir = Path(models_dir)
        logger.info("Initializing ArtifactRegistry from %s", models_dir)

        # Reset state before loading
        cls._model = None
        cls._encoders = {}
        cls._feature_columns = []
        cls._metadata = {}
        cls._loaded = False

        try:
            # Load churn model
            model_path = models_dir / "churn_model.pkl"
            if not model_path.exists():
                logger.warning("Missing artifact: %s", model_path)
                return
            cls._model = joblib.load(model_path)
            logger.info("Loaded churn model from %s", model_path)

            # Load label encoders
            encoders_path = models_dir / "label_encoders.pkl"
            if not encoders_path.exists():
                logger.warning("Missing artifact: %s", encoders_path)
                return
            cls._encoders = joblib.load(encoders_path)
            logger.info("Loaded label encoders from %s", encoders_path)

            # Load feature columns
            columns_path = models_dir / "feature_columns.pkl"
            if not columns_path.exists():
                logger.warning("Missing artifact: %s", columns_path)
                return
            cls._feature_columns = joblib.load(columns_path)
            logger.info("Loaded feature columns from %s", columns_path)

            # Load model metadata
            metadata_path = models_dir / "model_metadata.json"
            if not metadata_path.exists():
                logger.warning("Missing artifact: %s", metadata_path)
                return
            with open(metadata_path, "r", encoding="utf-8") as f:
                cls._metadata = json.load(f)
            logger.info("Loaded model metadata from %s", metadata_path)

            # All four files loaded successfully
            cls._loaded = True
            logger.info("ArtifactRegistry initialized successfully")

        except Exception as e:
            logger.error("Failed to load artifacts: %s", e)
            cls._model = None
            cls._encoders = {}
            cls._feature_columns = []
            cls._metadata = {}
            cls._loaded = False

    @classmethod
    def get_model(cls) -> Any:
        """Return the loaded churn model."""
        return cls._model

    @classmethod
    def get_encoders(cls) -> Dict[str, LabelEncoder]:
        """Return the dictionary of column name → fitted LabelEncoder."""
        return cls._encoders

    @classmethod
    def get_feature_columns(cls) -> List[str]:
        """Return the ordered list of feature column names."""
        return cls._feature_columns

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return the model metadata dictionary."""
        return cls._metadata

    @classmethod
    def is_loaded(cls) -> bool:
        """Return whether all artifacts are loaded and ready."""
        return cls._loaded

    @classmethod
    def cleanup(cls) -> None:
        """Reset all state to defaults, releasing loaded artifacts."""
        cls._model = None
        cls._encoders = {}
        cls._feature_columns = []
        cls._metadata = {}
        cls._loaded = False
        logger.info("ArtifactRegistry cleaned up")
