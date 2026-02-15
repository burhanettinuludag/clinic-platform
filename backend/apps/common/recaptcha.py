"""
Google reCAPTCHA v3 dogrulama.

Kullanim:
    from apps.common.recaptcha import verify_recaptcha
    if not verify_recaptcha(request.data.get('recaptcha_token'), 'login'):
        return Response({'error': 'Bot korumasi dogrulanamadi'}, status=400)

Settings:
    RECAPTCHA_SECRET_KEY = env('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_SCORE_THRESHOLD = 0.5
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'


def verify_recaptcha(token, expected_action=None):
    """
    reCAPTCHA v3 token dogrula.

    Args:
        token: Frontend'den gelen recaptcha token
        expected_action: Beklenen action (login, register, contact)

    Returns:
        bool: Dogrulama basarili mi
    """
    secret = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    if not secret:
        # Key yoksa development'ta bypass
        logger.warning('RECAPTCHA_SECRET_KEY not set, bypassing verification')
        return True

    if not token:
        logger.warning('reCAPTCHA token empty')
        return False

    try:
        resp = requests.post(VERIFY_URL, data={
            'secret': secret,
            'response': token,
        }, timeout=5)
        data = resp.json()

        if not data.get('success'):
            logger.warning(f"reCAPTCHA failed: {data.get('error-codes', [])}")
            return False

        score = data.get('score', 0)
        threshold = getattr(settings, 'RECAPTCHA_SCORE_THRESHOLD', 0.5)
        if score < threshold:
            logger.warning(f"reCAPTCHA low score: {score} < {threshold}")
            return False

        if expected_action and data.get('action') != expected_action:
            logger.warning(f"reCAPTCHA action mismatch: {data.get('action')} != {expected_action}")
            return False

        return True

    except Exception as e:
        logger.error(f"reCAPTCHA verify error: {e}")
        # Hata durumunda gecir (availability > security)
        return True
