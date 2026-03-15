import re
import logging
from django.utils import timezone
from django.core.cache import cache
from .models import AuditLog

logger = logging.getLogger('security')

# Sağlık verisi erişimi gerektiren URL pattern'leri - TÜM hastalık modülleri
HEALTH_DATA_PATTERNS = [
    r'/api/v1/tracking/',
    r'/api/v1/migraine/',
    r'/api/v1/epilepsy/',
    r'/api/v1/dementia/',
    r'/api/v1/wellness/',
    r'/api/v1/tasks/',
    r'/api/v1/doctor/patients/',
    r'/api/v1/chat/sessions/',
    r'/api/v1/notifications/',
    r'/api/v1/gamification/',
]

# Başarısız giriş denemelerini izle
LOGIN_PATTERNS = [
    r'/api/v1/auth/login/',
    r'/api/v1/auth/token/',
]

AUDITED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

# Hesap kilitleme ayarları
MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION = 900  # 15 dakika (saniye)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AccountLockoutMiddleware:
    """
    Brute-force saldırılarına karşı hesap kilitleme.
    5 başarısız girişten sonra IP'yi 15 dakika engeller.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.login_patterns = [re.compile(p) for p in LOGIN_PATTERNS]

    def __call__(self, request):
        # Sadece login endpointlerinde kontrol et
        if request.method == 'POST' and self._is_login_request(request):
            ip = get_client_ip(request)
            lockout_key = f'lockout:{ip}'
            attempts_key = f'login_attempts:{ip}'

            # Kilitli mi kontrol et
            if cache.get(lockout_key):
                from django.http import JsonResponse
                logger.warning(
                    f'SECURITY: Locked out IP attempted login: {ip}'
                )
                return JsonResponse(
                    {
                        'error': 'Çok fazla başarısız giriş denemesi. '
                        'Lütfen 15 dakika sonra tekrar deneyin.',
                        'error_en': 'Too many failed login attempts. '
                        'Please try again in 15 minutes.',
                        'locked': True,
                    },
                    status=429,
                )

            response = self.get_response(request)

            # Başarısız giriş mi kontrol et
            if response.status_code in (401, 403, 400):
                attempts = cache.get(attempts_key, 0) + 1
                cache.set(attempts_key, attempts, LOCKOUT_DURATION)

                if attempts >= MAX_FAILED_LOGINS:
                    cache.set(lockout_key, True, LOCKOUT_DURATION)
                    logger.warning(
                        f'SECURITY: IP locked out after {attempts} failed logins: {ip}'
                    )

                    # Audit log'a da yaz
                    try:
                        AuditLog.objects.create(
                            action='lockout',
                            resource_type='auth',
                            ip_address=ip,
                            details={
                                'reason': 'brute_force',
                                'attempts': attempts,
                                'lockout_duration': LOCKOUT_DURATION,
                                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                            },
                        )
                    except Exception:
                        pass

            elif response.status_code == 200:
                # Başarılı giriş - sayacı sıfırla
                cache.delete(attempts_key)
                cache.delete(lockout_key)

            return response

        return self.get_response(request)

    def _is_login_request(self, request):
        return any(p.search(request.path) for p in self.login_patterns)


class AuditLogMiddleware:
    """KVKK uyumu: Sağlık verisi erişimlerini denetim loguna yazar."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.compiled_patterns = [re.compile(p) for p in HEALTH_DATA_PATTERNS]

    def __call__(self, request):
        response = self.get_response(request)

        if not self._should_audit(request, response):
            return response

        try:
            self._create_log(request, response)
        except Exception as e:
            # Audit hatalarını sessizce yutma - loglama yap
            logger.error(f'KVKK AUDIT ERROR: {e} | path={request.path}')

        return response

    def _should_audit(self, request, response):
        if request.method not in AUDITED_METHODS:
            return False
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        if response.status_code >= 400:
            return False
        return any(p.search(request.path) for p in self.compiled_patterns)

    def _create_log(self, request, response):
        action_map = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }

        AuditLog.objects.create(
            user=request.user,
            action=action_map.get(request.method, request.method.lower()),
            resource_type=self._extract_resource_type(request.path),
            ip_address=get_client_ip(request),
            details={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            },
        )

    def _extract_resource_type(self, path):
        parts = path.strip('/').split('/')
        # /api/v1/tracking/... -> tracking
        # /api/v1/migraine/... -> migraine
        if len(parts) >= 3:
            return parts[2]
        return 'unknown'


class LastActiveMiddleware:
    """Kullanıcının son aktivite tarihini günceller."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, 'user') and request.user.is_authenticated:
            now = timezone.now()
            user = request.user
            # Her istekte değil, en az 5 dakikada bir güncelle
            if not user.last_active or (now - user.last_active).total_seconds() > 300:
                from django.contrib.auth import get_user_model
                get_user_model().objects.filter(pk=user.pk).update(last_active=now)

        return response
