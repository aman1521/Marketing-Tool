import asyncio
import logging
from pprint import pprint

# Atlas Mock
from backend.services.captain.diagnose.diagnosis_engine import CaptainDiagnosisEngine
from backend.services.captain.execute.execution_engine import CaptainExecuteEngine
from backend.services.atlas.signals.feature_engine import AtlasFeatureEngine
from backend.services.safety_engine.schemas import GenesisConstraintsSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("closed_loop_test")

async def run_closed_loop():
    logger.info("--- PHASE 3: CLOSED LOOP VALIDATION STARTED ---")
    
    # 1. MOCK ATLAS SIGNALS
    logger.info("1. Simulating Atlas Signals Payload...")
    mock_campaigns = [
         # Campaign 1: SCALING OPPORTUNITY
        {"campaign_id": "cmp_scale", "metrics": {"spend": 1000, "revenue": 3000}, "features": {"roas_1d": 3.0, "scaling_confidence_score": 0.85, "volatility_index": 0.05, "anomaly_score": 0.0, "ctr": 0.05, "conversion_gap_score": 0}},
        
         # Campaign 2: CONVERSION COLLAPSE
        {"campaign_id": "cmp_conv", "metrics": {"spend": 500, "revenue": 50}, "features": {"roas_1d": 0.1, "conversion_gap_score": 0.9, "ctr": 0.06, "volatility_index": 0.2, "anomaly_score": 0.0}},
        
         # Campaign 3: TRACKING/RISK VIOLATION
        {"campaign_id": "cmp_risk", "metrics": {"spend": 0, "revenue": 0}, "features": {"anomaly_score": 0.95, "volatility_index": 0.9}}
    ]
    
    benchmarks = {"roas_1d": {"percentile_50": 2.0}, "ctr": {"percentile_50": 0.015}}
    
    # 2. MOCK GENESIS CONSTRAINTS
    logger.info("2. Simulating Genesis Load...")
    genesis_constraints = {
        "max_budget_change_percent": 20.0,
        "max_daily_budget": 5000.0,
        "max_risk_score": 0.6,
        "auto_execution_enabled": True, # Needed to pass AutonomyGuard
        "creative_sandbox_required": True,
        "landing_page_auto_edit_allowed": False
    }
    
    # 3. CAPTAIN DIAGNOSE
    logger.info("3. Executing Captain Diagnose...")
    diagnose_engine = CaptainDiagnosisEngine()
    diagnosis = await diagnose_engine.run_hybird_diagnosis(mock_campaigns, benchmarks, {})
    
    logger.info(f"Diagnosis Result: {diagnosis['account_state']}, Config Score: {diagnosis['confidence_score']}, Risk: {diagnosis['risk_level']}")
    
    # 4. CAPTAIN STRATEGY (MOCKING ACTIONS BASED ON DIAGNOSIS)
    logger.info("4. Generating Strategy Actions...")
    
    proposed_actions = []
    
    for cap in diagnosis.get("campaign_breakdown", []):
         state = cap.get("campaign_state")
         cid = cap.get("campaign_id")
         if state == "SCALING_OPPORTUNITY":
             proposed_actions.append({
                 "action_type": "BUDGET_INCREASE",
                 "campaign_id": cid,
                 "platform": "meta",
                 "parameters": {"old_budget": 1000, "new_budget": 1150} # +15% (under 20% limit)
             })
         elif state == "CONVERSION_PROBLEM":
             proposed_actions.append({
                 "action_type": "PAUSE_CREATIVE",
                 "campaign_id": cid,
                 "platform": "google",
                 "parameters": {"ad_id": "ad_bad"}
             })
         elif state == "TRACKING_ISSUE":
             proposed_actions.append({
                 "action_type": "BUDGET_INCREASE",
                 "campaign_id": cid,
                 "platform": "tiktok",
                 "parameters": {"old_budget": 100, "new_budget": 500} # +400% (violates 20% limit & high anomaly)
             })
             
    # 5. CAPTAIN EXECUTE
    logger.info("5. Routing to Captain Execute (Autonomy Mode)...")
    execute_engine = CaptainExecuteEngine()
    
    diagnostic_context = {
         "risk_level": diagnosis.get("risk_level", "MODERATE"),
         "confidence_score": diagnosis.get("confidence_score", 0.0),
         "account_state": diagnosis.get("account_state")
    }
    
    # Mapping signals for Autonomy Guard check
    signal_map = {c["campaign_id"]: c["features"] for c in mock_campaigns}
    
    results = []
    for action in proposed_actions:
         features = signal_map.get(action["campaign_id"], {})
         # Send individually for explicit loop testing
         res = await execute_engine.execute_strategy([action], genesis_constraints, diagnostic_context, features)
         results.append(res)
         
    for r in results:
         logger.info(f"Execution Output: {r['executions']}")
         
    logger.info("--- CLOSED LOOP VALIDATION COMPLETE ---")

if __name__ == '__main__':
    asyncio.run(run_closed_loop())
