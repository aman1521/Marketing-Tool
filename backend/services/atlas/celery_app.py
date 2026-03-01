import os
from celery import Celery
from celery.schedules import crontab
import asyncio

# Setup Celery Configuration targeting Redis
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/1")
app = Celery('atlas_system', broker=redis_url, backend=redis_url)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Scheduled Triggers
app.conf.beat_schedule = {
    'nightly-platform-ingestion': {
        'task': 'backend.services.atlas.celery_app.run_nightly_sync',
        'schedule': crontab(hour=0, minute=0), # Execute at Midnight UTC
    },
    'benchmark-snapshot-calc': {
        'task': 'backend.services.atlas.celery_app.run_benchmarks',
        'schedule': crontab(day_of_week=0, hour=3), # Sunday 3 AM UTC
    }
}

@app.task
def run_nightly_sync():
    """
    Kicks off global company loops calling SyncOrchestrator over async loops.
    """
    from backend.services.atlas.main import async_session
    from backend.services.atlas.collect.sync_orchestrator import SyncOrchestrator
    
    async def process():
        async with async_session() as db:
            orchestrator = SyncOrchestrator(db)
            # In production, query list of Active Companies from central DB
            companies = ["cmp_1", "cmp_2"]
            for cmp in companies:
                await orchestrator.run_daily_sync(cmp)
                
    asyncio.run(process())

@app.task
def run_benchmarks():
    """Calculates industry averages in the background."""
    from backend.services.atlas.main import async_session
    from backend.services.atlas.benchmarks.benchmark_engine import AtlasBenchmarkEngine
    from backend.services.atlas.models import EngineeredFeatures
    from sqlalchemy import select
    
    async def process():
        async with async_session() as db:
            engine = AtlasBenchmarkEngine(db)
            result = await db.execute(select(EngineeredFeatures))
            records = result.scalars().all()
            if records:
                # E.g. execute across segments
                await engine.compute_industry_snapshot(records, "Ecommerce", "Mid-Market")

    asyncio.run(process())
