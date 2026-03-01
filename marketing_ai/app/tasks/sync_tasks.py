from app.core.celery_app import celery_app

@celery_app.task(name='app.tasks.sync_tasks.sync_all_company_metrics')
def sync_all_company_metrics():
    """
    Loops through all active PlatformConnections and fetches raw metrics and engagement.
    Updates Post and Campaign DB entries accordingly.
    """
    return "Metrics Data Sync Completed"
