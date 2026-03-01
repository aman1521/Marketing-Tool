import os
import sys

# Add project root to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.decision_engine.rules import DeterministicRulesEngine

def run_tests():
    print("--- Testing Decision Engine Rules ---")
    
    engine = DeterministicRulesEngine()
    
    # 1. Platform Fit Score
    metrics = {
        'normalized_roas_score': 85.0,
        'normalized_engagement_score': 60.0,
        'normalized_volume_score': 90.0,
        'normalized_growth_score': 40.0
    }
    score = engine.calculate_platform_fit_score(metrics)
    print(f"Platform Fit Score (Expected ~ 72): {score}")
    
    # 2. Budget Scaling
    action, scale = engine.evaluate_budget_scaling(roas=3.0, target_roas=2.0, spend_velocity=0.8)
    print(f"Budget Scaling Action: {action}, Scale Factor: {scale}")
    
    action, scale = engine.evaluate_budget_scaling(roas=1.5, target_roas=2.0, spend_velocity=1.0)
    print(f"Budget Scaling Action: {action}, Scale Factor: {scale}")
    
    # 3. Creative Replacement
    replace, msg = engine.evaluate_creative_replacement(creative_score=35, frequency=2.5, days_active=10)
    print(f"Replace Creative: {replace} -> {msg}")
    
    replace, msg = engine.evaluate_creative_replacement(creative_score=60, frequency=5.0, days_active=20)
    print(f"Replace Creative: {replace} -> {msg}")
    
    # 4. Risk Validation
    val = engine.apply_risk_validation(budget_change=1000, max_daily_budget=500)
    print(f"Risk Validated Change: {val} (Cap logic executed)")
    
if __name__ == "__main__":
    run_tests()
