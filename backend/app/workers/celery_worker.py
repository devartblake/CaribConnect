import os
import signal

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbit-mq:5672/")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_worker = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.services.tasks"]
)

celery_worker.conf.update(
    result_expires=3600,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default'
)

# Configure Celery with custom exchanges and queues using kombu.Queue and kombu.Exchange
celery_worker.conf.task_queues = (
    Queue('default', Exchange('default', type='direct'), routing_key='default'),
    Queue('payment_queue', Exchange('payment_exchange', type='direct'), routing_key='payment'),
    Queue('notification_queue', Exchange('notification_exchange', type='fanout'), routing_key=''),
)

# Optional: Define custom task routes
# celery_worker.conf.update(
#     task_routes={
#         'app.tasks.send_email': {'queue': 'email'},
#     },
# )


# Define your periodic tasks in the beat_schedule
celery_worker.conf.beat_schedule = {
    'send-email-notifications-every-minute': {
        'task': 'app.services.tasks.send_email_notifications',
        'schedule': crontab(),  # Every minute
    },
    'cleanup-old-records-every-hour': {
        'task': 'app.services.tasks.cleanup_old_records',
        'schedule': crontab(minute=0),  # Every hour
    },
    'generate-daily-report-at-midnight': {
        'task': 'app.services.tasks.generate_daily_report',
        'schedule': crontab(minute=0, hour=0),  # Every day at midnight
    },
    'heartbeat-check-every-five-minutes': {
        'task': 'app.services.tasks.heartbeat_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

# Optional: Handle graceful shutdown
def graceful_shutdown(signum, frame):
    celery_worker.control.shutdown()

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
