"""
Health check endpoint.
Deployment, monitoring ve uptime kontrolleri icin.
GET /api/v1/health/
"""

import time
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """Sistem sagligi kontrol endpoint'i."""
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []

    def get(self, request):
        # DB kontrol
        db_ok = True
        db_ms = 0
        try:
            start = time.time()
            with connection.cursor() as c:
                c.execute("SELECT 1")
            db_ms = round((time.time() - start) * 1000, 1)
        except Exception:
            db_ok = False

        status_code = 200 if db_ok else 503
        return Response({
            'status': 'ok' if db_ok else 'degraded',
            'database': {'ok': db_ok, 'response_ms': db_ms},
            'version': '1.0.0',
        }, status=status_code)
