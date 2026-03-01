import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
from shared.models.beanie_models import MLPrediction
from model_training.train import AIGrowthXGBoostModel

# ==========================================
# Phase 7.2 Automated Retraining Pipeline
# ==========================================

class ContinuousLearningPipeline:
    """
    Evaluates ML Drift and triggers re-training sequences if threshold breaks.
    (Self-healing behavior)
    """
    
    DRIFT_TOLERANCE_THRESHOLD = 0.15 # 15% Error variance triggers retraining

    @staticmethod
    async def evaluate_drift(business_id: uuid.UUID) -> bool:
        """
        Calculates average error rate over last 7 days.
        Returns True if retraining is required due to model drift.
        """
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_predictions = await MLPrediction.find(
            MLPrediction.business_id == business_id,
            MLPrediction.created_at >= seven_days_ago
        ).to_list()

        if not recent_predictions or len(recent_predictions) < 10:
            logger.info(f"Insufficient predictions for business {business_id} to evaluate drift.")
            return False

        error_sum = 0.0
        prediction_count = 0
        
        for pred in recent_predictions:
            if pred.error_rate is not None:
                error_sum += pred.error_rate
                prediction_count += 1
                
        if prediction_count == 0:
            return False

        avg_error = error_sum / prediction_count
        logger.info(f"Drift Analysis for {business_id}: Average Error is {avg_error*100:.2f}%")

        if avg_error > ContinuousLearningPipeline.DRIFT_TOLERANCE_THRESHOLD:
            logger.warning(f"MODEL DRIFT DETECTED (> {ContinuousLearningPipeline.DRIFT_TOLERANCE_THRESHOLD*100}%). Initiating Re-training Sequence...")
            return True
        else:
            logger.info("Model accuracy within acceptable tolerances. Retraining skipped.")
            return False

    @staticmethod
    async def trigger_retraining(business_id: uuid.UUID):
        """
        Instantiates a new XGBoost context and pushes new model weights 
        back into the storage container path.
        """
        logger.info(f"--- INITIATING RETRAINING PIPELINE FOR {business_id} ---")
        try:
            # 1. We would typically pull entire historical feature store here.
            # Using our mocked trainer from the ml_service Phase 2 implementation.
            model = AIGrowthXGBoostModel()
            
            # The model internally pulls from the mocked dataset
            model.train()
            
            # Re-saves the generated weights out
            model.save_model(f"models/xgb_roas_{business_id}_{datetime.utcnow().date()}.json")
            
            logger.info("RETRAINING SUCCESSFUL. New model weights committed.")
            
            # Note: We would insert a system notification or audit log here to alert the Agency Admin.
            
        except Exception as e:
            logger.error(f"RETRAINING FAILED: {str(e)}")


async def run_learning_cycle():
    """Main execution loop for Cron"""
    logger.info("STARTING CONTINUOUS LEARNING CRON JOB...")
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/aios_database")
    await init_mongo(mongo_url, [MLPrediction])

    # Sample Business UUID (In prod, we would iterate unique businesses)
    sample_business = uuid.UUID('12345678-1234-5678-1234-567812345678')
    
    needs_retraining = await ContinuousLearningPipeline.evaluate_drift(sample_business)
    
    if needs_retraining:
         await ContinuousLearningPipeline.trigger_retraining(sample_business)
         
    close_mongo()
    logger.info("LEARNING CYCLE COMPLETE.")


if __name__ == "__main__":
    asyncio.run(run_learning_cycle())
