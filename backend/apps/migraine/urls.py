from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MigraineAttackViewSet, MigraineTriggerViewSet

router = DefaultRouter()
router.register('attacks', MigraineAttackViewSet, basename='migraine-attack')
router.register('triggers', MigraineTriggerViewSet, basename='migraine-trigger')

urlpatterns = [
    path('', include(router.urls)),
]
