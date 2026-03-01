import os
from celery import Celery
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    "ai_marketing_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Example: Schedule daily run at midnight
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'daily-intelligence-cycle': {
        'task': 'worker.celery_worker.run_daily_intelligence_task',
        'schedule': crontab(hour=0, minute=0),
    },
}

@celery_app.task(name='worker.celery_worker.run_daily_intelligence_task')
def run_daily_intelligence_task():
    from app.services.scheduler.daily_tasks import trigger_daily_intelligence_cycle
    
    print("Initiating Celery Background Worker Task: Daily Intelligence Cycle")
    try:
        trigger_daily_intelligence_cycle()
        return "Intelligence Cycle completed successfully."
    except Exception as e:
        print(f"Error executing intelligence loop: {str(e)}")
        return f"Failed: {str(e)}"
