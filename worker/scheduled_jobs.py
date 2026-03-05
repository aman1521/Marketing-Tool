"""
Scheduled Celery Jobs (Beat)
============================
The physical heartbeat of the Autonomous OS. Automatically pushes companies
into the Intelligence Loop every N hours without ANY human intervention.
"""

from celery.schedules import crontab
from worker.celery_worker import celery_app, run_intelligence_cycle_task
import logging

logger = logging.getLogger(__name__)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Maps the internal cron-jobs the Engine uses to stay alive.
    """
    logger.info("[Celery Beat] Registering Engine Heartbeats...")

    # 1. The Global Poller: Every 2 hours, spin up the entire OS for critical companies
    sender.add_periodic_task(
        crontab(minute=0, hour="*/2"), 
        trigger_global_company_intelligence_sweep.s(),
        name="Global Company Intelligence Sweep"
    )

    # 2. Add specific rules (e.g. Daily creative genome encoding)
    # sender.add_periodic_task(crontab(minute=0, hour='3'), encode_daily_creatives.s())

@celery_app.task(name="worker.scheduled_jobs.trigger_global_company_intelligence_sweep")
def trigger_global_company_intelligence_sweep():
    """
    Queries the database for active subscribers and dispatches a dedicated 
    Intelligence Loop worker node for each of them in parallel.
    """
    logger.info("[Celery Beat] Sweep Initiated: Loading active companies...")
    
    # MOCK: Database Query
    active_companies = [
        {"id": "corp_saas_1", "industry": "B2B SaaS"},
        {"id": "corp_ecom_2", "industry": "Ecommerce"}
    ]
    
    for company in active_companies:
        logger.info(f"[Celery Beat] Dispatching Intelligence Engine for {company['id']}")
        # Dispatch individual async background worker tasks
        run_intelligence_cycle_task.delay(
            company_id=company["id"],
            industry=company["industry"],
            campaigns=[]  # Atlas connector normally pulls this internally inside the loop
        )
        
    return f"Triggered {len(active_companies)} OS Cycles."
