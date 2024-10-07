from fastapi import APIRouter, HTTPException
from app.models import Payment, User
from app.services.tasks import send_notification_task  # Celery tasks for both payment and notification
from sqlmodel import Session, select
from app.core.db import create_engine  # Database engine

router = APIRouter()

# Notification endpoint
@router.post("/notify/")
async def notify(user_id: str, message: str):
    # Trigger notification sending in background
    send_notification_task.delay(user_id, message)
    return {"status": "Notification queued"}