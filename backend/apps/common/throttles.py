"""
API Rate Limiting / Throttle classes.

Kategoriler:
- AnonBurst: Anonim kullanicilar icin kisa sureli limit (10/dk)
- AnonSustained: Anonim kullanicilar icin uzun sureli limit (100/saat)
- UserBurst: Auth kullanicilar icin kisa sureli (30/dk)
- UserSustained: Auth kullanicilar icin uzun sureli (500/saat)
- AuthRateThrottle: Login/register brute-force korumasi (5/dk)
- AIAgentThrottle: AI agent cagrilari icin (10/saat)
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, SimpleRateThrottle


class AnonBurstThrottle(AnonRateThrottle):
    """Anonim - kisa sureli: 10 istek/dakika."""
    scope = 'anon_burst'


class AnonSustainedThrottle(AnonRateThrottle):
    """Anonim - uzun sureli: 100 istek/saat."""
    scope = 'anon_sustained'


class UserBurstThrottle(UserRateThrottle):
    """Auth user - kisa sureli: 30 istek/dakika."""
    scope = 'user_burst'


class UserSustainedThrottle(UserRateThrottle):
    """Auth user - uzun sureli: 500 istek/saat."""
    scope = 'user_sustained'


class AuthRateThrottle(SimpleRateThrottle):
    """Login/register brute-force korumasi: 5 istek/dakika per IP."""
    scope = 'auth'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class AIAgentThrottle(UserRateThrottle):
    """AI agent cagrilari: 10 istek/saat per user."""
    scope = 'ai_agent'
