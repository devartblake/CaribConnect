from sqlmodel import Session, engine, select

from app.models import Notification, User
from app.workers.celery_worker import celery_worker


@celery_worker.task(name="send_notification_task")
def send_notification_task(user_id: str, message: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()

        if not user:
            return {"error": "User not found"}

        # Create a new notification
        notification = Notification(user_id=user_id, message=message)
        session.add(notification)
        session.commit()

        print(f"Notification sent to {user.email}: {message}")
        return {"status": "Notification sent", "user_id": user_id, "message": message}
