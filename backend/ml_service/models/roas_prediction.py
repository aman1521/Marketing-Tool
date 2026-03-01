from .base_model import MLModel
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ROASPredictionModel(MLModel):
    """
    ROAS Prediction using XGBoost Regressor.
    Predicts Return on Ad Spend based on budget, duration, past performance, and intent features.
    """

    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="roas_prediction", version=version)
        
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train XGBoost regressor predicting ROAS.
        Required columns: 'budget', 'duration_days', 'clicks', 'impressions', 'intent_strength', 'audience_profit_score', 'actual_roas'
        """
        required_features = ['budget', 'duration_days', 'clicks', 'impressions', 'intent_strength', 'audience_profit_score']
        target = 'actual_roas'
        
        # Ensure columns exist, fill missing
        for col in required_features + [target]:
            if col not in data.columns:
                logger.warning(f"Missing column '{col}' for training, filling with default zeroes")
                data[col] = 0.0

        X = data[required_features].fillna(0)
        y = data[target].fillna(0)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        logger.info(f"Training ROAS Prediction model on {len(X_train)} records")
        
        self.model = xgb.XGBRegressor(
            n_estimators=100, 
            learning_rate=0.1, 
            max_depth=5, 
            random_state=42, 
            objective='reg:squarederror'
        )
        self.model.fit(X_train, y_train)
        
        # Calculate simplistic RMSE on test set
        preds = self.model.predict(X_test)
        rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
        
        self.is_trained = True
        logger.info(f"ROAS Prediction training complete. RMSE: {rmse}")
        
        return {
            "status": "success",
            "rmse": rmse,
            "feature_importances": dict(zip(required_features, [float(v) for v in self.model.feature_importances_]))
        }

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict ROAS for a given campaign setup
        """
        if not self.is_trained:
            logger.warning("Model is not trained, attempting to load from disk...")
            if not self.load():
                logger.error("No trained model available.")
                # We can fallback to a heuristic estimation
                budget = float(features.get('budget', 1000))
                intent_strength = float(features.get('intent_strength', 0.5))
                audience_profit_score = float(features.get('audience_profit_score', 50))
                
                # Simple heuristic ROAS
                base_roas = 1.0 + (intent_strength * 1.5) + (audience_profit_score / 100.0)
                # Diminishing returns on budget loosely applied
                scale_penalty = min(0.5, budget / 10000.0) 
                
                estimated_roas = max(0.01, base_roas - scale_penalty)
                
                return {
                    "predicted_roas": round(estimated_roas, 2),
                    "confidence": 0.0,
                    "reason": "Fallbacked to heuristic logic."
                }
                
        # Parse features
        feature_names = ['budget', 'duration_days', 'clicks', 'impressions', 'intent_strength', 'audience_profit_score']
        
        # Defaulting mid-values for missing metrics
        input_data = {
            'budget': [float(features.get('budget', 500))],
            'duration_days': [float(features.get('duration_days', 7))],
            'clicks': [float(features.get('clicks', 150))],
            'impressions': [float(features.get('impressions', 10000))],
            'intent_strength': [float(features.get('intent_strength', 0.5))],
            'audience_profit_score': [float(features.get('audience_profit_score', 50))]
        }
        
        df = pd.DataFrame(input_data, columns=feature_names)
        
        predicted_roas = max(0.01, float(self.model.predict(df)[0]))
        
        return {
            "predicted_roas": round(predicted_roas, 2),
            "confidence": 0.85 # Mocked static confidence measure for regressor limit
        }
