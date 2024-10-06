import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.helpers.task_helpers import (
    check_system_health,
    cleanup_old_records_db,
    clear_cache,
    create_backup,
    fetch_api_data,
    generate_report_db,
    update_cache,
)
from app.models import Notification, Record, User
from app.workers.celery_worker import celery_worker

from .email_service import send_email  # Assuming you have an email service
from .message_queue import send_message

logger = logging.getLogger(__name__)

@celery_worker.task
def process_payment(payment_id: int, amount: float, user_id: int):
    # Simulate payment processing
    time.sleep(5)  # Simulate a long-running task
    # Implement your payment processing logic here
    print(f"Processed payment with ID: {payment_id} for {user_id} with amount {amount}")
    return {"status": "success", "payment_id": payment_id, "amount": amount}

@celery_worker.task
def refund_payment(payment_id: int, amount: float):
    print(f"Refunding payment {payment_id} for amount {amount}")
    return {"status": "refunded", "payment_id": payment_id, "amount": amount}

@celery_worker.task
def send_email_task(email: str, subject: str, body: str):
    send_email(email, subject, body)
    print(f"Sent email to {email}")
    return {"status": "email_sent", "email": email}

@celery_worker.task
def send_notification_task(user_id: int, message: str):
    # Fetch user from the database
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": "user_not_found", "user_id": user_id}

# Create notification in the database
    notification = Notification(user_id=user.id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Send message to RabbitMQ queue
    send_message("notifications", message)
    print(f"Sent notification to user {user_id}: {message}")
    return {"status": "notification_sent", "user_id": user_id, "message": message}

@celery_worker.task
def generate_report(report_id: int):
    # Simulate report generation
    time.sleep(10)  # Simulate a long-running task
    # Implement your report generation logic here
    print(f"Generated report with ID: {report_id}")
    return {"status": "report_generated", "report_id": report_id}

@celery_worker.task
def cloeanup_old_records():
    """
    Cleans up old records from the database.
    This task runs every hour as scheduled in beat_schedule.
    """
    logger.info("Starting cleanup of old records...")

    try:
        cutoff_date = datetime.now() - timedelta(days=30)  # Example: Delete records older than 30 days
        records_deleted = cleanup_old_records_db(cutoff_date)  # Implement this function in your database module
        logger.info(f"Deleted {records_deleted} old records from the database.")
    except Exception as e:
        logger.error(f"Error during cleanup of old records: {e}")

    logger.info("Finished cleanup of old records.")

@celery_worker.task
def backup_database():
    # Logic to create a backup of the database
    create_backup()
    print("Database backup completed.")

@celery_worker.task
def refresh_cache():
    # Logic to refresh cached data
    clear_cache()
    update_cache()
    print("Cache refreshed.")

@celery_worker.task
def generate_daily_report():
    """
    Generates a daily report.
    This task runs every day at midnight as scheduled in beat_schedule.
    """
    logger.info("Generating daily report...")

    try:
        report = generate_report_db()  # Implement this function in your database module
        logger.info("Daily report generated successfully.")

        # Optionally, send the report via email
        send_email("admin@example.com", "Daily Report", report)  # Customize the recipient and content
        logger.info("Daily report sent to admin via email.")
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")

    logger.info("Finished generating daily report.")

@celery_worker.task
def heartbeat_check():
    """
    Performs a heartbeat check for the system.
    This task runs every five minutes as scheduled in beat_schedule.
    """
    logger.info("Performing heartbeat check...")

    try:
        # Implement your heartbeat check logic
        # For example, check database connection, API availability, etc.
        is_healthy = check_system_health()  # You need to implement this function
        if is_healthy:
            logger.info("System is healthy.")
        else:
            logger.warning("System health check failed!")
    except Exception as e:
        logger.error(f"Error during heartbeat check: {e}")

    logger.info("Finished heartbeat check.")

@celery_worker.task
def poll_external_api():
    """
    Celery task to poll an external API and log the result as a Record.
    """
    api_url = 'https://api.example.com/data'
    data = fetch_api_data(api_url)

    db = SessionLocal()
    try:
        if data:
            # Log the successful API call
            record = Record(action="API Poll", description="Fetched data successfully", status="Success")
        else:
            # Log the failed API call
            record = Record(action="API Poll", description="Failed to fetch data", status="Failure")

        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

