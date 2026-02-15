import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='apps.gamification.tasks.daily_streak_check')
def daily_streak_check():
    """Streak'leri kontrol et - 2 gun giris yapmayanlarin streak'ini sifirla."""
    from apps.gamification.models import UserStreak
    from datetime import timedelta

    yesterday = timezone.now().date() - timedelta(days=1)
    expired = UserStreak.objects.filter(
        is_active=True,
        last_activity_date__lt=yesterday,
    )
    count = expired.count()
    expired.update(is_active=False)
    logger.info(f"Reset {count} expired streaks")
    return {'reset': count}
