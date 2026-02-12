from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeizureEventViewSet, EpilepsyTriggerViewSet

router = DefaultRouter()
router.register('seizures', SeizureEventViewSet, basename='seizure-event')
router.register('triggers', EpilepsyTriggerViewSet, basename='epilepsy-trigger')

urlpatterns = [
    path('', include(router.urls)),
]
