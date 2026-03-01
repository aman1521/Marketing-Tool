from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class MLModel(ABC):
    """Abstract base class for all ML Models in the ML Service"""
    
    def __init__(self, model_name: str, version: str = "1.0"):
        self.model_name = model_name
        self.version = version
        self.is_trained = False
        self.model = None
        
        # Determine paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(self.base_dir, "saved_models")
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, f"{self.model_name}_v{self.version}.joblib")

    @abstractmethod
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the model and return metrics"""
        pass

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate prediction from features"""
        pass

    def save(self) -> bool:
        """Save the trained model to disk"""
        if not self.is_trained or self.model is None:
            logger.error(f"Cannot save {self.model_name}: model not trained")
            return False
        
        try:
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model {self.model_name} saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model {self.model_name}: {e}")
            return False

    def load(self) -> bool:
        """Load the model from disk if it exists"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                logger.info(f"Model {self.model_name} loaded from {self.model_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                return False
        else:
            logger.warning(f"No saved model found for {self.model_name} at {self.model_path}")
            return False
