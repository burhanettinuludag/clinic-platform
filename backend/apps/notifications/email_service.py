"""
Email bildirim servisi.

Notification olusturuldugunda, kullanicinin tercihine gore email gonderir.
Console backend (development) veya SMTP (production) kullanir.

Kullanim:
    from apps.notifications.email_service import send_notification_email
    send_notification_email(notification)
"""

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Bildirim tipi -> email tercihi eslesmesi
TYPE_TO_PREF = {
    'info': 'email_reminders',
    'alert': 'email_reminders',
    'reminder': 'email_reminders',
    'system': 'email_product_updates',
}

# Email HTML template
EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 0">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
  <tr><td style="background:#1e40af;padding:24px 32px">
    <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600">Norosera</h1>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 12px;color:#1f2937;font-size:18px;font-weight:600">{title}</h2>
    <p style="margin:0 0 24px;color:#4b5563;font-size:15px;line-height:1.6">{message}</p>
    {action_button}
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
    <p style="margin:0;color:#9ca3af;font-size:12px">Bu email Norosera platformu tarafindan otomatik gonderilmistir.</p>
  </td></tr>
  <tr><td style="background:#f9fafb;padding:16px 32px;text-align:center">
    <p style="margin:0;color:#9ca3af;font-size:11px">&copy; 2026 Norosera - Noroloji Klinigi</p>
  </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

ACTION_BUTTON = """<a href="{url}" style="display:inline-block;background:#1e40af;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:500">{label}</a>"""


def _should_send_email(user, notification_type):
    """Kullanicinin email tercihini kontrol et."""
    try:
        prefs = user.notification_preferences
        pref_field = TYPE_TO_PREF.get(notification_type, 'email_reminders')
        return getattr(prefs, pref_field, True)
    except Exception:
        # Tercih kaydi yoksa default True
        return True


def _build_html(title, message, action_url=None):
    """Email HTML olustur."""
    action_btn = ''
    if action_url:
        site_url = getattr(settings, 'SITE_URL', 'https://norosera.com')
        full_url = site_url + action_url if action_url.startswith('/') else action_url
        action_btn = ACTION_BUTTON.format(url=full_url, label='Goruntule')

    return EMAIL_TEMPLATE.format(
        title=title,
        message=message,
        action_button=action_btn,
    )


def send_notification_email(notification):
    """
    Notification objesine gore email gonder.

    Args:
        notification: Notification model instance

    Returns:
        bool: Email gonderildi mi
    """
    user = notification.recipient

    # Email tercihi kontrol
    if not _should_send_email(user, notification.notification_type):
        logger.debug(f"Email skipped for {user.email}: preference disabled")
        return False

    # Email adresi kontrol
    if not user.email:
        logger.warning(f"Email skipped: user {user.id} has no email")
        return False

    # TR tercih et
    title = notification.title_tr or notification.title_en
    message = notification.message_tr or notification.message_en

    try:
        html = _build_html(title, message, notification.action_url)
        plain = strip_tags(f"{title}\n\n{message}")

        send_mail(
            subject=f"[Norosera] {title}",
            message=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html,
            fail_silently=False,
        )
        logger.info(f"Email sent to {user.email}: {title}")
        return True

    except Exception as e:
        logger.error(f"Email failed for {user.email}: {e}")
        return False


def send_bulk_notification_emails(notifications):
    """Toplu email gonderimi."""
    sent = 0
    for n in notifications:
        if send_notification_email(n):
            sent += 1
    return sent
