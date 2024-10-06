from fastapi import APIRouter

from app.services.tasks import (
    send_notification_task,  # Celery tasks for both payment and notification
)

router = APIRouter()

# Notification endpoint
@router.post("/notify/")
async def notify(user_id: str, message: str):
    # Trigger notification sending in background
    send_notification_task.delay(user_id, message)
    return {"status": "Notification queued"}
