"""
Celery Worker Node
==================
Distributed background worker for the Marketing OS.
Continuously runs autonomous intelligence loops safely separated from the active HTTP API Server.
"""

import os
import asyncio
import logging
from celery import Celery
from typing import List, Dict, Any

from backend.services.intelligence.orchestrator.main_loop import UnifiedIntelligenceOrchestrator

logger = logging.getLogger(__name__)

# Basic Celery Config (Defaults to local Redis, production uses ElastiCache/RabbitMQ)
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery("marketing_engine_worker", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

@celery_app.task(bind=True, name="worker.celery_worker.run_intelligence_cycle_task")
def run_intelligence_cycle_task(self, company_id: str, industry: str, campaigns: List[Dict[str, Any]] = None):
    """
    Celery task that boots the Unified Intelligence Orchestrator.
    Since execute_intelligence_loop is async, we run it inside a synchronously wrapped asyncio event loop.
    """
    logger.info(f"[Celery Worker] Starting Autonomous Cycle for {company_id} [Task ID: {self.request.id}]")
    
    if campaigns is None:
        campaigns = []
        
    # We must bridge asynchronous AI calls inside standard Celery Sync execution.
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    orchestrator = UnifiedIntelligenceOrchestrator()
        
    # Execute the OS Brain
    try:
        result = loop.run_until_complete(
            orchestrator.execute_intelligence_loop(
                company_id=company_id,
                industry=industry,
                current_campaigns=campaigns
            )
        )
        logger.info(f"[Celery Worker] Finished Autonomous Cycle for {company_id} | Status: {result.get('status')}")
        return result
    except Exception as e:
        logger.error(f"[Celery Worker] Core OS Crash during Cycle: {e}")
        self.retry(exc=e, countdown=60) # Auto retry after 1 minute on failure
