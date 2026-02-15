import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name='apps.notifications.tasks.cleanup_old_notifications')
def cleanup_old_notifications():
    """90 gunluk okunmus bildirimleri temizle."""
    from apps.notifications.models import Notification
    cutoff = timezone.now() - timedelta(days=90)
    count, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {count} old notifications")
    return {'deleted': count}


@shared_task(name='apps.notifications.tasks.send_notification_email_async')
def send_notification_email_async(user_id, notification_type, title, message, action_url=None):
    """Bildirim emailini async gonder."""
    from apps.accounts.models import CustomUser
    from apps.notifications.email_service import send_notification_email
    try:
        user = CustomUser.objects.get(id=user_id)
        send_notification_email(user, notification_type, title, message, action_url)
        return {'sent': True, 'user_id': str(user_id)}
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {'sent': False, 'error': str(e)}
