"""
Dementia notification helper functions.
Uses the existing apps.notifications infrastructure.
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def _create_notification(user, notification_type, title_tr, title_en, message_tr, message_en, action_url=''):
    """Create a notification and optionally send email."""
    from apps.notifications.models import Notification
    from apps.notifications.tasks import send_notification_email_async

    notification = Notification.objects.create(
        recipient=user,
        notification_type=notification_type,
        title_tr=title_tr,
        title_en=title_en,
        message_tr=message_tr,
        message_en=message_en,
        action_url=action_url,
    )

    # Send email async
    try:
        send_notification_email_async.delay(
            user_id=str(user.id),
            notification_type=notification_type,
            title=title_tr,
            message=message_tr,
            action_url=action_url,
        )
    except Exception as e:
        logger.warning(f"Failed to queue email for {user.email}: {e}")

    return notification


def notify_exercise_reminder(patient):
    """Remind patient to do exercises (daily at 19:00 if no exercise today)."""
    return _create_notification(
        user=patient,
        notification_type='reminder',
        title_tr='Bugun egzersiz yapmadiniz!',
        title_en='You haven\'t exercised today!',
        message_tr='Bilissel sagliginiz icin bugun en az bir egzersiz tamamlamanizi oneririz.',
        message_en='We recommend completing at least one exercise today for your cognitive health.',
        action_url='/patient/dementia',
    )


def notify_streak_milestone(patient, days):
    """Congratulate patient on exercise streak."""
    return _create_notification(
        user=patient,
        notification_type='info',
        title_tr=f'Tebrikler! {days} gunluk seri!',
        title_en=f'Congratulations! {days} day streak!',
        message_tr=f'Art arda {days} gun egzersiz yaptiniz. Harika gidiyorsunuz!',
        message_en=f'You\'ve exercised for {days} consecutive days. Keep it up!',
        action_url='/patient/dementia?tab=progress',
    )


def notify_score_decline(patient, old_score, new_score):
    """Alert about cognitive score decline (also notify assigned doctor)."""
    from apps.accounts.models import PatientProfile

    _create_notification(
        user=patient,
        notification_type='alert',
        title_tr='Bilissel skorunuzda dusus tespit edildi',
        title_en='Cognitive score decline detected',
        message_tr=f'Bilissel skorunuz {old_score:.0f}\'dan {new_score:.0f}\'a dustu. '
                   f'Doktorunuza basvurmanizi oneririz.',
        message_en=f'Your cognitive score dropped from {old_score:.0f} to {new_score:.0f}. '
                   f'We recommend consulting your doctor.',
        action_url='/patient/dementia?tab=progress',
    )

    # Also notify doctor if assigned
    try:
        profile = PatientProfile.objects.get(user=patient)
        if profile.assigned_doctor:
            _create_notification(
                user=profile.assigned_doctor,
                notification_type='alert',
                title_tr=f'{patient.get_full_name()} - Bilissel skor dususu',
                title_en=f'{patient.get_full_name()} - Cognitive score decline',
                message_tr=f'Hastaniz {patient.get_full_name()}\'in bilissel skoru '
                           f'{old_score:.0f}\'dan {new_score:.0f}\'a dustu.',
                message_en=f'Your patient {patient.get_full_name()}\'s cognitive score '
                           f'dropped from {old_score:.0f} to {new_score:.0f}.',
            )
    except PatientProfile.DoesNotExist:
        pass


def notify_caregiver_alert(caregiver, patient, alert_type, details=''):
    """Send alert to caregiver about patient."""
    alert_messages = {
        'fall': {
            'title_tr': f'{patient.get_full_name()} - Dusme olayi',
            'title_en': f'{patient.get_full_name()} - Fall incident',
            'msg_tr': f'Hastaniz {patient.get_full_name()} icin dusme olayi kaydedildi.',
            'msg_en': f'A fall incident was recorded for {patient.get_full_name()}.',
        },
        'wandering': {
            'title_tr': f'{patient.get_full_name()} - Kaybolma/gezinme',
            'title_en': f'{patient.get_full_name()} - Wandering incident',
            'msg_tr': f'Hastaniz {patient.get_full_name()} icin kaybolma/gezinme olayi kaydedildi.',
            'msg_en': f'A wandering incident was recorded for {patient.get_full_name()}.',
        },
        'medication': {
            'title_tr': f'{patient.get_full_name()} - Ilac atlama',
            'title_en': f'{patient.get_full_name()} - Missed medication',
            'msg_tr': f'Hastaniz {patient.get_full_name()} icin ilac atlama kaydedildi.',
            'msg_en': f'A missed medication was recorded for {patient.get_full_name()}.',
        },
    }

    msg = alert_messages.get(alert_type, {
        'title_tr': f'{patient.get_full_name()} - Uyari',
        'title_en': f'{patient.get_full_name()} - Alert',
        'msg_tr': f'Hastaniz {patient.get_full_name()} ile ilgili bir uyari var. {details}',
        'msg_en': f'There is an alert about your patient {patient.get_full_name()}. {details}',
    })

    return _create_notification(
        user=caregiver,
        notification_type='alert',
        title_tr=msg['title_tr'],
        title_en=msg['title_en'],
        message_tr=msg['msg_tr'],
        message_en=msg['msg_en'],
        action_url='/caregiver/dashboard',
    )
