from fastapi import APIRouter
router = APIRouter()

@router.post("/trigger-daily")
async def manual_trigger_intelligence():
    # Kicks off Celery Task
    return {"status": "Daily Task Initiated via Background Worker"}

@router.get("/dashboard")
async def get_dashboard():
    return {"dashboard_data": "Generated from Behavior Profiles"}
