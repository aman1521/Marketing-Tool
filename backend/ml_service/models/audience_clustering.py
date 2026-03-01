from .base_model import MLModel
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AudienceClusteringModel(MLModel):
    """
    Audience Clustering using K-Means.
    Groups customers into distinct clusters and maps them to profitability scores based on historical ROAS.
    """

    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="audience_clustering", version=version)
        self.scaler = None
        self.cluster_profitability_map = {}
        self.n_clusters = 5
        
        # Load the components if they exist
        import os, joblib
        self.scaler_path = os.path.join(self.model_dir, f"{self.model_name}_scaler_v{self.version}.joblib")
        self.metadata_path = os.path.join(self.model_dir, f"{self.model_name}_meta_v{self.version}.joblib")
        
    def load(self) -> bool:
        """Override to load scaler and metadata as well"""
        loaded_model = super().load()
        import os, joblib
        if loaded_model:
            try:
                if os.path.exists(self.scaler_path):
                    self.scaler = joblib.load(self.scaler_path)
                if os.path.exists(self.metadata_path):
                    self.cluster_profitability_map = joblib.load(self.metadata_path)
                return True
            except Exception as e:
                logger.error(f"Failed to load supplementary artifacts for {self.model_name}: {e}")
                return False
        return False
        
    def save(self) -> bool:
        """Override to save scaler and metadata"""
        saved = super().save()
        import joblib
        if saved:
            try:
                if self.scaler:
                    joblib.dump(self.scaler, self.scaler_path)
                joblib.dump(self.cluster_profitability_map, self.metadata_path)
                logger.info("Saved supplementary artifacts for audience clustering model.")
                return True
            except Exception as e:
                logger.error(f"Failed to save supplementary artifacts: {e}")
                return False
        return False

    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train K-Means clustering
        Required columns: 'age', 'income', 'past_purchases', 'total_spend', 'avg_session_length', 'historical_roas'
        """
        required_features = ['age', 'income', 'past_purchases', 'total_spend', 'avg_session_length']
        
        # Ensure columns exist, fill missing
        for col in required_features + ['historical_roas']:
            if col not in data.columns:
                logger.warning(f"Missing column '{col}' for training, filling with default zeroes/means")
                data[col] = 0.0

        X = data[required_features].fillna(0)
        
        logger.info(f"Training Audience Clustering model on {len(data)} records")
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        clusters = self.model.fit_predict(X_scaled)
        
        # Calculate cluster profitability map
        data['cluster'] = clusters
        mean_roas_by_cluster = data.groupby('cluster')['historical_roas'].mean()
        
        # Scale into a profitability score out of 100 for easy interpretation
        max_roas = mean_roas_by_cluster.max() if mean_roas_by_cluster.max() > 0 else 1
        
        for cluster_id in range(self.n_clusters):
            roas = mean_roas_by_cluster.get(cluster_id, 0)
            score = min(max(int((roas / max_roas) * 100), 10), 100) # Base 10 score minimum
            self.cluster_profitability_map[cluster_id] = {
                "roas_multiplier": round(float(roas), 2),
                "profitability_score": score
            }
            
        self.is_trained = True
        logger.info(f"Training complete. Cluster Profitability Mapping: {self.cluster_profitability_map}")
        
        return {
            "status": "success",
            "clusters": self.n_clusters,
            "inertia": float(self.model.inertia_),
            "cluster_mapping": self.cluster_profitability_map
        }

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict cluster for a single user/cohort and return profitability estimation
        """
        if not self.is_trained:
            logger.warning("Model is not trained, attempting to load from disk...")
            if not self.load():
                logger.error("No trained model available.")
                # We can fallback to a default
                return {
                    "cluster_id": -1,
                    "profitability_score": 50,
                    "roas_multiplier": 1.0,
                    "confidence": 0.0,
                    "reason": "Model untrained."
                }
                
        # Parse features into pandas DataFrame for scaling
        feature_names = ['age', 'income', 'past_purchases', 'total_spend', 'avg_session_length']
        
        # Extract features (defaulting to middle-ground values if missing)
        input_data = {
            'age': [float(features.get('age', 35))],
            'income': [float(features.get('income', 60000))],
            'past_purchases': [float(features.get('past_purchases', 2))],
            'total_spend': [float(features.get('total_spend', 150.0))],
            'avg_session_length': [float(features.get('avg_session_length', 120.0))]
        }
        
        df = pd.DataFrame(input_data, columns=feature_names)
        
        X_scaled = self.scaler.transform(df)
        cluster_id = int(self.model.predict(X_scaled)[0])
        
        # Get distances to cluster centers to compute a "confidence" metric
        distances = self.model.transform(X_scaled)[0]
        closest_dist = distances[cluster_id]
        
        # Basic confidence inversion mapping (closer = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 / (1.0 + float(closest_dist))))
        
        cluster_info = self.cluster_profitability_map.get(cluster_id, {
            "roas_multiplier": 1.0,
            "profitability_score": 50
        })
        
        # Factor in intent features if passed down from ML service integration
        roas_multiplier = cluster_info["roas_multiplier"]
        profit_score = cluster_info["profitability_score"]
        
        if "intent_strength" in features:
            intent_strength = float(features.get("intent_strength", 0.5))
            # Boost roas multiplier up to 1.5x based on intent, limit to 0.8x if low intent
            intent_boost = 0.5 + float(intent_strength)
            roas_multiplier *= intent_boost
            
        return {
            "cluster_id": cluster_id,
            "profitability_score": profit_score,
            "roas_multiplier": round(roas_multiplier, 2),
            "confidence": round(confidence, 2)
        }
