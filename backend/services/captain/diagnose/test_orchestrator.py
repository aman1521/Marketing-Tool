import os
import sys
import asyncio
import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.services.captain.diagnose.orchestrator_main import merge_intelligence, OrchestrationRequest
from backend.services.captain.strategy.llm_strategy import LLMStrategyGenerator

async def run_tests():
    print("--- Testing Intelligence Orchestrator ---")
    
    # 1. Test LLM Strategy Generation directly
    print("\n[1] LLM Strategy Generator")
    llm = LLMStrategyGenerator()
    biz_ctx = {
        "name": "Test Brand",
        "monthly_budget": 50000,
        "target_roas": 2.5
    }
    mock_ml = [
        {"model_type": "roas_prediction", "prediction": 3.1, "confidence": 0.9},
        {"model_type": "creative_performance", "prediction": 88, "confidence": 0.8}
    ]
    mock_intent = {
        "intent_segment": "Ready to Buy",
        "intent_strength": 0.92
    }
    prompt = llm.build_system_prompt(biz_ctx, mock_ml, mock_intent)
    print("PROMPT LENGTH:", len(prompt))
    print("PREVIEW:\n", prompt)
    
    # 2. Test the core Orchestrator Logic
    # We will simulate the request object directly
    print("\n[2] Orchestrator Main Endpoint Logic")
    req = OrchestrationRequest(
        business_context=biz_ctx,
        ml_predictions=mock_ml,
        behavior_intent=mock_intent
    )
    
    # NOTE: Since the Decision Engine running at http://decision_engine:8007 might not be 
    # running in purely local python test mode, it'll gracefully fallback in merge_intelligence.
    output = await merge_intelligence("biz-123", req)
    
    print("\nFINAL ORCHESTRATED STRATEGY OBJECT:")
    print("Business ID:", output.get("business_id"))
    print("Decision:", output.get("deterministic_decision"))
    print("LLM Note:", output.get("llm_strategy"))
    print("Risk Flags:", output.get("risk_flags"))
    
if __name__ == "__main__":
    asyncio.run(run_tests())
