from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

from services.admin_views import pipeline_run_view

from apps.common.views_health import HealthCheckView
from apps.common.views_contact import ContactFormView

# Admin branding
admin.site.site_header = 'Norosera Yonetim Paneli'
admin.site.site_title = 'Norosera Admin'
admin.site.index_title = 'Yonetim'

_schema_view = SpectacularAPIView.as_view()
_swagger_view = SpectacularSwaggerView.as_view(url_name='schema')
_redoc_view = SpectacularRedocView.as_view(url_name='schema')

# Production'da API docs sadece staff erişimli
if not settings.DEBUG:
    _schema_view = staff_member_required(_schema_view)
    _swagger_view = staff_member_required(_swagger_view)
    _redoc_view = staff_member_required(_redoc_view)

urlpatterns = [
    path('api/v1/health/', HealthCheckView.as_view(), name='health-check'),
    path('api/v1/contact/', ContactFormView.as_view(), name='contact-form'),
    path(f"{settings.ADMIN_URL}pipeline/", pipeline_run_view, name="pipeline_run"),
    path(settings.ADMIN_URL, admin.site.urls),
    # API Documentation (production'da staff-only)
    path('api/schema/', _schema_view, name='schema'),
    path('api/docs/', _swagger_view, name='swagger-ui'),
    path('api/redoc/', _redoc_view, name='redoc'),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/users/', include('apps.accounts.urls_profile')),
    path('api/v1/modules/', include('apps.patients.urls')),
    path('api/v1/tasks/', include('apps.patients.urls_tasks')),
    path('api/v1/tracking/', include('apps.tracking.urls')),
    path('api/v1/migraine/', include('apps.migraine.urls')),
    path('api/v1/epilepsy/', include('apps.epilepsy.urls')),
    path('api/v1/dementia/', include('apps.dementia.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/doctor/', include('apps.doctor_panel.urls')),
    path('api/v1/kvkk/', include('apps.common.urls')),
    path('api/v1/site/', include('apps.common.urls_site')),
    path('api/v1/wellness/', include('apps.wellness.urls')),
    path('api/v1/gamification/', include('apps.gamification.urls')),
    path('api/v1/social/', include('apps.social.urls')),
]

# Store & Payments: sadece DEBUG modda aktif (production'da gecici olarak kapali)
if settings.DEBUG:
    urlpatterns += [
        path('api/v1/store/', include('apps.store.urls')),
        path('api/v1/payments/', include('apps.payments.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
