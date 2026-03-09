"""
Dementia report sharing via Email and Telegram.
Handles KVKK-compliant report distribution to patient-defined recipients.
"""

import logging
import requests
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)

# KVKK disclosure text appended to all shared reports
KVKK_NOTICE_TR = (
    "Bu rapor, hasta tarafindan tanimlanan aliciya KVKK kapsaminda "
    "acik riza ile paylasilmistir. Rapordaki bilgilerin ucuncu kisilerle "
    "paylasilmasi yasaktir."
)

SHARE_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 0">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
  <tr><td style="background:#1e40af;padding:24px 32px">
    <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600">Norosera - Bilissel Saglik Raporu</h1>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 12px;color:#1f2937;font-size:18px;font-weight:600">{recipient_name},</h2>
    <p style="margin:0 0 16px;color:#4b5563;font-size:15px;line-height:1.6">
      {patient_name} tarafindan bilissel saglik raporu sizinle paylasildi.
    </p>
    <p style="margin:0 0 8px;color:#4b5563;font-size:14px">
      <strong>Rapor donemi:</strong> {start_date} - {end_date}
    </p>
    <p style="margin:0 0 24px;color:#4b5563;font-size:14px">
      Rapor PDF olarak bu emaile eklenmistir.
    </p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
    <p style="margin:0 0 8px;color:#6b7280;font-size:12px;line-height:1.5">
      <strong>KVKK Bilgilendirmesi:</strong> {kvkk_notice}
    </p>
    <p style="margin:0;color:#9ca3af;font-size:11px">
      Bu email Norosera platformu tarafindan otomatik gonderilmistir.
    </p>
  </td></tr>
  <tr><td style="background:#f9fafb;padding:16px 32px;text-align:center">
    <p style="margin:0;color:#9ca3af;font-size:11px">&copy; 2026 Norosera - Noroloji Klinigi</p>
  </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def _create_share_record(patient, recipient, share_type, start_date, end_date,
                         ip_address=None, success=True, error_message=''):
    """Create audit record for KVKK compliance."""
    from apps.dementia.models import ReportShareRecord
    from apps.common.models import AuditLog

    record = ReportShareRecord.objects.create(
        patient=patient,
        recipient=recipient,
        share_type=share_type,
        report_period_start=start_date,
        report_period_end=end_date,
        ip_address=ip_address,
        success=success,
        error_message=error_message,
    )

    # Also log to global audit log
    AuditLog.objects.create(
        user=patient,
        action='share_report',
        resource_type='ReportShareRecord',
        resource_id=record.id,
        ip_address=ip_address,
        details={
            'recipient_name': recipient.name,
            'recipient_email': recipient.email,
            'share_type': share_type,
            'period': f"{start_date} - {end_date}",
        },
    )

    return record


def share_report_via_email(patient, recipient, start_date, end_date, ip_address=None):
    """
    Generate and send a cognitive health report via email.

    Args:
        patient: User instance (patient)
        recipient: ReportRecipient instance
        start_date: date - report period start
        end_date: date - report period end
        ip_address: str - for KVKK audit

    Returns:
        dict with success status and message
    """
    from apps.dementia.reports import DementiaReportGenerator

    if not recipient.email:
        return {'success': False, 'error': 'Alicinin email adresi tanimli degil.'}

    try:
        # Generate PDF report
        generator = DementiaReportGenerator(
            user=patient,
            start_date=start_date,
            end_date=end_date,
        )
        buffer = generator.generate()
        pdf_content = buffer.getvalue()

        # Build email
        patient_name = patient.get_full_name() or patient.email
        html_body = SHARE_EMAIL_TEMPLATE.format(
            recipient_name=recipient.name,
            patient_name=patient_name,
            start_date=start_date.strftime('%d.%m.%Y'),
            end_date=end_date.strftime('%d.%m.%Y'),
            kvkk_notice=KVKK_NOTICE_TR,
        )

        filename = f"bilissel_rapor_{patient.last_name}_{start_date}_{end_date}.pdf"

        email = EmailMessage(
            subject=f"[Norosera] {patient_name} - Bilissel Saglik Raporu",
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        email.content_subtype = 'html'
        email.attach(filename, pdf_content, 'application/pdf')
        email.send(fail_silently=False)

        # Record share
        _create_share_record(
            patient=patient,
            recipient=recipient,
            share_type='email',
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address,
        )

        logger.info(f"Report shared via email: {patient.email} -> {recipient.email}")
        return {'success': True, 'message': f'Rapor {recipient.email} adresine gonderildi.'}

    except Exception as e:
        logger.error(f"Email share failed: {patient.email} -> {recipient.email}: {e}")

        _create_share_record(
            patient=patient,
            recipient=recipient,
            share_type='email',
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address,
            success=False,
            error_message=str(e),
        )

        return {'success': False, 'error': f'Email gonderilemedi: {str(e)}'}


def share_report_via_telegram(patient, recipient, start_date, end_date, ip_address=None):
    """
    Generate and send a cognitive health report via Telegram bot.

    Requires TELEGRAM_BOT_TOKEN in settings.
    Recipient must have telegram_chat_id set (obtained via /start command to bot).

    Returns:
        dict with success status and message
    """
    from apps.dementia.reports import DementiaReportGenerator

    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not bot_token:
        return {'success': False, 'error': 'Telegram bot token yapilandirilmamis.'}

    if not recipient.telegram_chat_id:
        return {'success': False, 'error': 'Alicinin Telegram chat ID\'si tanimli degil.'}

    try:
        # Generate PDF report
        generator = DementiaReportGenerator(
            user=patient,
            start_date=start_date,
            end_date=end_date,
        )
        buffer = generator.generate()
        pdf_content = buffer.getvalue()

        patient_name = patient.get_full_name() or patient.email
        filename = f"bilissel_rapor_{patient.last_name}_{start_date}_{end_date}.pdf"

        # Caption message
        caption = (
            f"Norosera - Bilissel Saglik Raporu\n\n"
            f"Hasta: {patient_name}\n"
            f"Donem: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n\n"
            f"KVKK: {KVKK_NOTICE_TR}"
        )

        # Telegram Bot API - sendDocument
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {
            'document': (filename, BytesIO(pdf_content), 'application/pdf'),
        }
        data = {
            'chat_id': recipient.telegram_chat_id,
            'caption': caption[:1024],  # Telegram caption limit
        }

        response = requests.post(url, data=data, files=files, timeout=30)
        result = response.json()

        if not result.get('ok'):
            raise Exception(result.get('description', 'Telegram API hatasi'))

        # Record share
        _create_share_record(
            patient=patient,
            recipient=recipient,
            share_type='telegram',
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address,
        )

        logger.info(f"Report shared via Telegram: {patient.email} -> {recipient.telegram_chat_id}")
        return {'success': True, 'message': 'Rapor Telegram uzerinden gonderildi.'}

    except Exception as e:
        logger.error(f"Telegram share failed: {patient.email} -> {recipient.telegram_chat_id}: {e}")

        _create_share_record(
            patient=patient,
            recipient=recipient,
            share_type='telegram',
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address,
            success=False,
            error_message=str(e),
        )

        return {'success': False, 'error': f'Telegram gonderilemedi: {str(e)}'}
