from celery import Celery
from ..core.config import settings

celery_app = Celery(
    "booking_system",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=["app.tasks.booking_tasks", "app.tasks.notification_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "cleanup-expired-bookings": {
            "task": "app.tasks.booking_tasks.cleanup_expired_bookings",
            "schedule": 300.0,  # каждые 5 минут
        },
        "send-reminder-notifications": {
            "task": "app.tasks.notification_tasks.send_booking_reminders",
            "schedule": 3600.0,  # каждый час
        },
    }
)