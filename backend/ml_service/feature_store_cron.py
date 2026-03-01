import asyncio
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

logger = logging.getLogger(__name__)

class FeatureStorePipeline:
    """
    Automated pipeline to aggregate, compute, and store periodic ML features.
    """
    def __init__(self):
        self.is_running = False
        
    async def extract_raw_signals(self):
        """Simulate extracting raw data traces from PostgreSQL logs or Platform APIs."""
        logger.info("Extracting raw platform logs from PostgreSQL...")
        await asyncio.sleep(1) # Simulation
        return []

    async def compute_features(self, raw_data):
        """Calculates ROAS, intent thresholds, retention curves to store in feature set."""
        logger.info("Computing macro-level ML features (Rolling ROAS, LTV aggregates)...")
        await asyncio.sleep(1)
        return {"updated": True, "count": 150}

    async def update_feature_store(self, features):
        """Save feature sets to persistent MongoDB storage via Beanie/Motor."""
        logger.info("Persisting computed feature set to robust volume store.")
        await asyncio.sleep(1)
        # Mocking Beanie Model insert via placeholder
        try:
            # e.g., await bm.MLPrediction.insert_many(...)
            pass
        except Exception as e:
            logger.error(f"Failed to persist features: {e}")

    async def run_cycle(self):
        """Executes a single pipeline cycle."""
        logger.info(f"--- Starting Feature Store Update Cycle at {datetime.utcnow().isoformat()} ---")
        try:
            raw_data = await self.extract_raw_signals()
            features = await self.compute_features(raw_data)
            await self.update_feature_store(features)
            logger.info("--- Feature Store Sync Complete ---")
        except Exception as e:
            logger.error(f"Error during feature store cycle: {e}")

async def start_cron_scheduler(interval_seconds: int = 3600):
    """
    Loops indefinitely, calling the pipeline every interval_seconds.
    Suitable to be run alongside the FastAPI async lifecycle or as a standalone cron worker.
    """
    pipeline = FeatureStorePipeline()
    pipeline.is_running = True
    
    # Initialize DB (Assuming running standalone here; in FastAPI, lifespan handles it)
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.MLPrediction, bm.Business, bm.User])
    except Exception as e:
        logger.warning(f"Feature Cron: Failed to connect to DB: {e}")

    logger.info(f"Starting Feature Store cron scheduler. Interval: {interval_seconds}s")
    
    try:
        while pipeline.is_running:
            await pipeline.run_cycle()
            logger.info(f"Cron sleeping for {interval_seconds} seconds.")
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Feature Store cron scheduler terminated.")
    finally:
        try:
            close_mongo()
        except Exception:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        # Run quickly once for debugging if executed directly
        asyncio.run(start_cron_scheduler(interval_seconds=10))
    except KeyboardInterrupt:
        logger.info("Exiting...")
