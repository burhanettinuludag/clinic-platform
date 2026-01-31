from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceView

router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')
router.register('settings', NotificationPreferenceView, basename='notification-preference')

urlpatterns = [
    path('', include(router.urls)),
]
