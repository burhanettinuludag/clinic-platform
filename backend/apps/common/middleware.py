import re
from django.utils import timezone
from .models import AuditLog

# Sağlık verisi erişimi gerektiren URL pattern'leri
HEALTH_DATA_PATTERNS = [
    r'/api/v1/tracking/',
    r'/api/v1/migraine/',
    r'/api/v1/tasks/',
    r'/api/v1/doctor/patients/[\w-]+/timeline/',
    r'/api/v1/doctor/patients/[\w-]+/notes/',
]

AUDITED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


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
        except Exception:
            pass  # Audit failure should not break the request

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
