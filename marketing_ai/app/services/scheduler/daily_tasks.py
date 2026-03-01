import os
import asyncio
from typing import Dict, Any, List

# Imports for intelligence pipeline
from app.services.connector_framework.meta_connector import MetaConnector
from app.services.connector_framework.google_connector import GoogleConnector
from app.services.intelligence.feature_engineering import FeatureEngineering
from app.services.intelligence.behavior_model import BehaviorModel
from app.services.intelligence.ai_reasoning import AIReasoningLayer
from app.services.intelligence.safety_engine import SafetyEngine
from app.services.intelligence.execution_engine import ExecutionEngine
import logging

logger = logging.getLogger(__name__)

# Note: Celery runs tasks synchronously, though we can use asyncio.run 
# if invoking async DB operations inside the worker. Using synchronous wrapper:

def trigger_daily_intelligence_cycle():
    """
    Main background job orchestrator to run every 24 hours.
    (Wrapped by Celery task in worker/celery_worker.py)
    """
    asyncio.run(_run_intelligence_cycle_async())

async def _run_intelligence_cycle_async():
    """
    The actual sequence architecture specified in the mega-prompt.
    """
    logger.info("Initializing Daily Intelligence Cycle")

    # In a real environment we fetch active companies using app.database session:
    # companies = await active_companies()
    mock_active_company = {"id": "comp_12345", "active_platforms": ["meta", "google"]}
    
    # Instantiate necessary engines
    reasoner = AIReasoningLayer()
    safety = SafetyEngine()
    execution_engine = ExecutionEngine()
    feature_eng = FeatureEngineering()
    behavior_model = BehaviorModel()
    
    logger.info(f"Processing Company: {mock_active_company['id']}")
    
    # 1. Pull metrics from connectors
    meta = MetaConnector(company_id=mock_active_company["id"], platform_name="meta", credentials_payload={})
    raw_metrics_store = await meta.fetch_metrics("account_abc", date_start="2026-02-27", date_end="2026-02-28")
    
    # 2. Store raw metrics
    # await _store_metrics_db(raw_metrics_store)
    
    # 3. Run feature engineering (also integrates AirLLM tagging)
    engineered = await feature_eng.process_raw_to_features(raw_metrics_store)
    
    # 4. Run behavior model
    behavior = await behavior_model.calculate_segment_models(engineered)
    
    # 5. Call AI Reasoning
    strategy = await reasoner.generate_strategy(
        company_business_context={"industry": "SaaS", "goal": "ROAS 3.0"},
        historical_performance_json=behavior
    )
    
    # Iterate and Validate
    proposed_actions = strategy.get("proposed_actions", [])
    for action in proposed_actions:
        
        # 6. Pass output through safety engine
        status, reason = safety.validate_ai_action(action)
        logger.info(f"AI Safety check: {status} | Reason: {reason}")
        
        # 7. Execute approved actions
        if status == "approved":
            await execution_engine.execute(mock_active_company["id"], action)
            # 8. Log Everything to DB (ExecutionLog table)
        elif status == "requires_manual_review":
            await execution_engine.queue_for_approval(mock_active_company["id"], action, reason)
        else:
            logger.warning(f"Action Rejected: {action['type']}")
    
    logger.info("Daily cycle completed. All actions logged.")
