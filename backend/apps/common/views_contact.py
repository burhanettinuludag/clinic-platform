"""
Public contact form endpoint.
POST /api/v1/contact/

reCAPTCHA v3 korumalı.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.common.recaptcha import verify_recaptcha
from apps.common.throttles import AnonBurstThrottle

logger = logging.getLogger(__name__)


class ContactFormView(APIView):
    """Public iletisim formu."""
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [AnonBurstThrottle]

    def post(self, request):
        # reCAPTCHA
        if not verify_recaptcha(request.data.get('recaptcha_token'), 'contact'):
            return Response({'error': 'Bot korumasi dogrulanamadi.'}, status=400)

        name = strip_tags(request.data.get('name', '')).strip()
        email = strip_tags(request.data.get('email', '')).strip()
        subject = strip_tags(request.data.get('subject', '')).strip()
        message = strip_tags(request.data.get('message', '')).strip()

        # Validation
        errors = {}
        if not name or len(name) < 2:
            errors['name'] = 'Isim zorunludur (min 2 karakter).'
        if not email or '@' not in email:
            errors['email'] = 'Gecerli bir email adresi giriniz.'
        if not subject or len(subject) < 3:
            errors['subject'] = 'Konu zorunludur (min 3 karakter).'
        if not message or len(message) < 10:
            errors['message'] = 'Mesaj zorunludur (min 10 karakter).'
        if len(message) > 5000:
            errors['message'] = 'Mesaj 5000 karakterden uzun olamaz.'

        if errors:
            return Response({'errors': errors}, status=400)

        # Email gonder
        try:
            admin_email = getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)
            send_mail(
                subject=f'[Norosera Iletisim] {subject}',
                message=f'Gonderen: {name} <{email}>\nKonu: {subject}\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            logger.info(f"Contact form: {name} <{email}> - {subject}")
        except Exception as e:
            logger.error(f"Contact form email error: {e}")

        return Response({'success': True, 'message': 'Mesajiniz alindi. En kisa surede donus yapacagiz.'})
