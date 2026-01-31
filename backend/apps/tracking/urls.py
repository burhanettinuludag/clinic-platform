from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SymptomDefinitionViewSet,
    SymptomEntryViewSet,
    MedicationViewSet,
    MedicationLogViewSet,
    ReminderConfigViewSet,
)

router = DefaultRouter()
router.register('symptom-definitions', SymptomDefinitionViewSet, basename='symptom-definition')
router.register('symptoms', SymptomEntryViewSet, basename='symptom-entry')
router.register('medications', MedicationViewSet, basename='medication')
router.register('medication-logs', MedicationLogViewSet, basename='medication-log')
router.register('reminders', ReminderConfigViewSet, basename='reminder-config')

urlpatterns = [
    path('', include(router.urls)),
]
