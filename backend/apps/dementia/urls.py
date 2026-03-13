from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CognitiveExerciseViewSet,
    ExerciseSessionViewSet,
    DailyAssessmentViewSet,
    CaregiverNoteViewSet,
    CognitiveScoreViewSet,
    CognitiveScreeningViewSet,
    CaregiverDashboardViewSet,
    RelativeDashboardViewSet,
    ReportRecipientViewSet,
)

router = DefaultRouter()
router.register('exercises', CognitiveExerciseViewSet, basename='cognitive-exercise')
router.register('sessions', ExerciseSessionViewSet, basename='exercise-session')
router.register('assessments', DailyAssessmentViewSet, basename='daily-assessment')
router.register('notes', CaregiverNoteViewSet, basename='caregiver-note')
router.register('scores', CognitiveScoreViewSet, basename='cognitive-score')
router.register('screening', CognitiveScreeningViewSet, basename='cognitive-screening')
router.register('recipients', ReportRecipientViewSet, basename='report-recipient')

# Caregiver routes (separate router to avoid slug conflicts)
caregiver_router = DefaultRouter()
caregiver_router.register('caregiver', CaregiverDashboardViewSet, basename='caregiver-dashboard')

# Relative routes (read-only access for patient relatives)
relative_router = DefaultRouter()
relative_router.register('relative', RelativeDashboardViewSet, basename='relative-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(caregiver_router.urls)),
    path('', include(relative_router.urls)),
]
