"""
Celery application configuration for clinic-platform.
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('clinic_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Periodic tasks (celery-beat)
app.conf.beat_schedule = {
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0),  # Her gun 03:00
    },
    'send-medication-reminders': {
        'task': 'apps.tracking.tasks.send_medication_reminders',
        'schedule': crontab(minute='*/15'),  # Her 15 dakika
    },
    'update-weather-cache': {
        'task': 'apps.wellness.tasks.update_weather_cache',
        'schedule': crontab(minute=0, hour='*/3'),  # Her 3 saat
    },
    'daily-streak-check': {
        'task': 'apps.gamification.tasks.daily_streak_check',
        'schedule': crontab(hour=0, minute=30),  # Her gun 00:30
    },
}
