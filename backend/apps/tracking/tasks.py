import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='apps.tracking.tasks.send_medication_reminders')
def send_medication_reminders():
    """Aktif ilac hatirlatmalarini kontrol et ve bildirim gonder."""
    from apps.tracking.models import ReminderConfig
    from apps.notifications.models import Notification

    now = timezone.localtime()
    current_time = now.time()
    current_day = now.weekday()

    # 15 dakika aralikla calistigi icin +/- 7 dakika window
    from datetime import timedelta, datetime
    window_start = (datetime.combine(now.date(), current_time) - timedelta(minutes=7)).time()
    window_end = (datetime.combine(now.date(), current_time) + timedelta(minutes=7)).time()

    reminders = ReminderConfig.objects.filter(
        is_enabled=True,
        time_of_day__gte=window_start,
        time_of_day__lte=window_end,
    )

    sent = 0
    for r in reminders:
        if current_day in (r.days_of_week or []):
            # Bugun zaten gonderilmis mi?
            already = Notification.objects.filter(
                recipient=r.patient,
                notification_type='reminder',
                created_at__date=now.date(),
                metadata__reminder_id=str(r.id),
            ).exists()
            if not already:
                Notification.objects.create(
                    recipient=r.patient,
                    notification_type='reminder',
                    title_tr=r.title,
                    title_en=r.title,
                    message_tr=f"Hatirlat: {r.title}",
                    message_en=f"Reminder: {r.title}",
                    metadata={'reminder_id': str(r.id), 'reminder_type': r.reminder_type},
                )
                sent += 1

    logger.info(f"Sent {sent} medication reminders")
    return {'sent': sent}
