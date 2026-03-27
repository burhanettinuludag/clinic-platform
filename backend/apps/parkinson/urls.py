from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('triggers', views.ParkinsonTriggerViewSet, basename='parkinson-trigger')
router.register('symptoms', views.ParkinsonSymptomViewSet, basename='parkinson-symptom')
router.register('medications', views.ParkinsonMedicationViewSet, basename='parkinson-medication')
router.register('medication-logs', views.ParkinsonMedicationLogViewSet, basename='parkinson-med-log')
router.register('assessments/hoehn-yahr', views.HoehnYahrViewSet, basename='hoehn-yahr')
router.register('assessments/schwab-england', views.SchwabEnglandViewSet, basename='schwab-england')
router.register('assessments/nmsquest', views.NMSQuestViewSet, basename='nmsquest')
router.register('assessments/motor', views.NoseraMotorViewSet, basename='nosera-motor')
router.register('assessments/daily-living', views.NoseraDailyLivingViewSet, basename='nosera-daily')
router.register('visits', views.ParkinsonVisitViewSet, basename='parkinson-visit')
router.register('dashboard', views.ParkinsonDashboardView, basename='parkinson-dashboard')

urlpatterns = [
    path(
        'medications/<uuid:medication_pk>/schedules/',
        views.MedicationScheduleViewSet.as_view({
            'get': 'list', 'post': 'create',
        }),
        name='medication-schedules-list',
    ),
    path(
        'medications/<uuid:medication_pk>/schedules/<uuid:pk>/',
        views.MedicationScheduleViewSet.as_view({
            'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='medication-schedules-detail',
    ),
    path('', include(router.urls)),
]
