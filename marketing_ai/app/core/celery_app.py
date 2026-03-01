from celery import Celery
import os
from celery.schedules import crontab

# Configure Celery to use Redis as broker and backend
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "marketing_saas",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    # Here we define the modules where Celery should look for tasks
    include=["app.tasks.automation_tasks", "app.tasks.sync_tasks"]
)

# Optional config settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

# Setting up Celery Beat (Cron jobs for automation)
celery_app.conf.beat_schedule = {
    'run-daily-automations': {
        'task': 'app.tasks.automation_tasks.execute_daily_auto_mode',
        'schedule': crontab(hour=0, minute=0), # Run daily at midnight UTC
        'args': ()
    },
    'sync-platform-metrics-hourly': {
        'task': 'app.tasks.sync_tasks.sync_all_company_metrics',
        'schedule': crontab(minute=0), # Run every hour on the hour
        'args': ()
    }
}
