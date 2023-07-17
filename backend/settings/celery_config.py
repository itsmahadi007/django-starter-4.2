# settings/celery.py
from celery.schedules import crontab

CELERY_TIMEZONE = "UTC"

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    "mail_blasting": {
        "task": "apps.notification_manager.tasks.mail_blast",  # Replace with your task function
        "schedule": crontab(minute="*/1"),  # Replace with your desired schedule
    },
}
