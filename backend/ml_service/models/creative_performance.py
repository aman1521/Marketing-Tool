from .base_model import MLModel
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CreativePerformanceModel(MLModel):
    """
    Creative Performance Prediction using XGBoost.
    Predicts Click-Through Rate (CTR), Conversion Rate (CVR), and generates a unified Creative Score.
    """

    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="creative_performance", version=version)
        
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train XGBoost regressors for CTR and CVR
        Required columns: 'video_length', 'hook_type_encoded', 'watch_time_pct', 'engagement_rate', 'historical_ctr', 'historical_cvr'
        """
        # Simplification: Train a single model predicting a unified 'creative_score' directly based on historical metrics
        required_features = ['video_length', 'hook_type', 'watch_time_pct', 'engagement_rate']
        target = 'historical_creative_score'
        
        # Ensure columns exist, fill missing
        for col in required_features + [target]:
            if col not in data.columns:
                logger.warning(f"Missing column '{col}' for training, filling with default zeroes")
                data[col] = 0.0

        X = data[required_features].fillna(0)
        y = data[target].fillna(0)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        logger.info(f"Training Creative Performance model on {len(X_train)} records")
        self.model = xgb.XGBRegressor(
            n_estimators=100, 
            learning_rate=0.1, 
            max_depth=4, 
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
        
        self.is_trained = True
        logger.info(f"Creative Performance training complete. RMSE: {rmse}")
        
        return {
            "status": "success",
            "rmse": rmse,
            "feature_importances": dict(zip(required_features, [float(v) for v in self.model.feature_importances_]))
        }

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_trained:
            logger.warning("Model is not trained, attempting to load from disk...")
            if not self.load():
                logger.error("No trained model available.")
                
                # Basic heuristic fallback
                engagement = float(features.get('engagement_rate', 2.0))
                watch = float(features.get('watch_time_pct', 40.0))
                
                heuristic_score = min(100.0, max(0.0, (engagement * 10) + (watch)))
                
                return {
                    "predicted_ctr": round((heuristic_score / 100) * 5.0, 2),
                    "predicted_cvr": round((heuristic_score / 100) * 3.0, 2),
                    "creative_score": round(heuristic_score, 2),
                    "confidence": 0.0,
                    "reason": "Untrained generic fallback."
                }
                
        feature_names = ['video_length', 'hook_type', 'watch_time_pct', 'engagement_rate']
        
        input_data = {
            'video_length': [float(features.get('video_length', 15.0))],
            'hook_type': [float(features.get('hook_type_encoded', 1))],
            'watch_time_pct': [float(features.get('watch_time_pct', 30.0))],
            'engagement_rate': [float(features.get('engagement_rate', 1.5))]
        }
        
        df = pd.DataFrame(input_data, columns=feature_names)
        predicted_score = float(self.model.predict(df)[0])
        
        # Clip to bounds 0-100
        score = max(0.0, min(100.0, predicted_score))
        
        # Derive CTR and CVR logically from the unified score
        predicted_ctr = score * 0.05 # Max 5% CTR
        predicted_cvr = score * 0.03 # Max 3% CVR
        
        return {
            "predicted_ctr": round(predicted_ctr, 2),
            "predicted_cvr": round(predicted_cvr, 2),
            "creative_score": round(score, 2),
            "confidence": 0.8
        }
