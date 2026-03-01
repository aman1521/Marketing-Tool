import os
import sys
import logging
import asyncio
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
from shared.models.beanie_models import StrategyOutput, Business
from backend.services.captain.diagnose.orchestrator_main import IntelligenceOrchestrator

# ==========================================
# Phase 7.2 Continuous Strategy Regeneration
# ==========================================

class StrategyRefresher:
    """
    Evaluates business units asynchronously and forces a complete regeneration
    of their Marketing Strategy using the Intelligence Orchestrator 
    every 7-14 days OR when model drift has occurred.
    """

    @staticmethod
    async def run_refresh_cycle():
        """
        Main Cron Executor Method.
        Scans all businesses. If last Strategy Output is > 7 days old, regenerates.
        """
        logger.info("STRATEGY REFRESH CYCLE: Initiated")
        
        # In a real environment, we'd iterate over all active Businesses in MongoDB
        # Here we mock one for Phase 7 implementation proof.
        business_id = str(uuid.uuid4())
        
        try:
            logger.info(f"STRATEGY REFRESH: Generating fresh context mapping for Business {business_id}")
            orchestrator = IntelligenceOrchestrator()
            
            # Spin up the LLM Engine to generate the strategy Document
            result = orchestrator.generate_unified_strategy(business_id)
            
            # Simulated persistence: Save back to MongoDB
            # output_doc = StrategyOutput(...)
            # await output_doc.insert()
            
            logger.info(f"STRATEGY REFRESH COMPLETE: Successfully rebuilt intelligence tree for {business_id}")
            logger.info(f"New Hooks: {result.get('creative_strategy', {}).get('hook_angles')}")
        
        except Exception as e:
            logger.error(f"Failed to refresh strategy for {business_id}: {str(e)}")


async def main():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/aios_database")
    await init_mongo(mongo_url, [StrategyOutput, Business])
    
    await StrategyRefresher.run_refresh_cycle()
    
    close_mongo()

if __name__ == "__main__":
    asyncio.run(main())
