import os
import sys
import pandas as pd
import numpy as np

# Add project root to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.ml_service.models.audience_clustering import AudienceClusteringModel
from backend.ml_service.models.roas_prediction import ROASPredictionModel
from backend.ml_service.models.budget_optimization import BudgetOptimizationModel
from backend.ml_service.models.creative_performance import CreativePerformanceModel

def generate_mock_audience_data():
    np.random.seed(42)
    return pd.DataFrame({
        'age': np.random.randint(18, 65, 100),
        'income': np.random.normal(60000, 15000, 100),
        'past_purchases': np.random.randint(0, 10, 100),
        'total_spend': np.random.exponential(100, 100),
        'avg_session_length': np.random.normal(120, 30, 100),
        'historical_roas': np.random.normal(2.5, 0.5, 100)
    })

def generate_mock_roas_data():
    np.random.seed(42)
    return pd.DataFrame({
        'budget': np.random.uniform(100, 5000, 100),
        'duration_days': np.random.randint(3, 30, 100),
        'clicks': np.random.randint(10, 1000, 100),
        'impressions': np.random.randint(1000, 50000, 100),
        'intent_strength': np.random.uniform(0, 1, 100),
        'audience_profit_score': np.random.randint(10, 100, 100),
        'actual_roas': np.random.normal(2.0, 0.8, 100)
    })

def generate_mock_creative_data():
    np.random.seed(42)
    return pd.DataFrame({
        'video_length': np.random.uniform(5, 60, 100),
        'hook_type': np.random.randint(0, 5, 100),
        'watch_time_pct': np.random.uniform(10, 90, 100),
        'engagement_rate': np.random.uniform(0.5, 5.0, 100),
        'historical_creative_score': np.random.normal(50, 20, 100)
    })

def test_audience_clustering():
    print("\n--- Testing Audience Clustering ---")
    model = AudienceClusteringModel()
    mock_data = generate_mock_audience_data()
    train_res = model.train(mock_data)
    print("Train Res:", train_res)
    
    predict_res = model.predict({'age': 25, 'income': 50000})
    print("Predict Res:", predict_res)

def test_roas_prediction():
    print("\n--- Testing ROAS Prediction ---")
    model = ROASPredictionModel()
    mock_data = generate_mock_roas_data()
    train_res = model.train(mock_data)
    print("Train Res:", train_res)
    
    predict_res = model.predict({'budget': 1000, 'intent_strength': 0.8})
    print("Predict Res:", predict_res)

def test_creative_performance():
    print("\n--- Testing Creative Performance ---")
    model = CreativePerformanceModel()
    mock_data = generate_mock_creative_data()
    train_res = model.train(mock_data)
    print("Train Res:", train_res)
    
    predict_res = model.predict({'video_length': 15, 'engagement_rate': 2.5})
    print("Predict Res:", predict_res)

def test_budget_optimization():
    print("\n--- Testing Budget Optimization ---")
    model = BudgetOptimizationModel()
    features = {
        'total_budget': 1000,
        'campaigns': [
            {'id': 'c1', 'predicted_roas': 2.5},
            {'id': 'c2', 'predicted_roas': 1.2},
            {'id': 'c3', 'predicted_roas': 0.8},
            {'id': 'c4', 'predicted_roas': 3.1}
        ]
    }
    predict_res = model.predict(features)
    print("Predict Res:", predict_res)

if __name__ == "__main__":
    test_audience_clustering()
    test_roas_prediction()
    test_creative_performance()
    test_budget_optimization()
    print("\nAll ML models tested successfully!")
