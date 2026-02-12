from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/users/', include('apps.accounts.urls_profile')),
    path('api/v1/modules/', include('apps.patients.urls')),
    path('api/v1/tasks/', include('apps.patients.urls_tasks')),
    path('api/v1/tracking/', include('apps.tracking.urls')),
    path('api/v1/migraine/', include('apps.migraine.urls')),
    path('api/v1/epilepsy/', include('apps.epilepsy.urls')),
    path('api/v1/dementia/', include('apps.dementia.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/store/', include('apps.store.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/doctor/', include('apps.doctor_panel.urls')),
    path('api/v1/kvkk/', include('apps.common.urls')),
    path('api/v1/wellness/', include('apps.wellness.urls')),
    path('api/v1/gamification/', include('apps.gamification.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
