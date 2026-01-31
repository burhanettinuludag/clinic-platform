from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CognitiveExerciseViewSet,
    ExerciseSessionViewSet,
    DailyAssessmentViewSet,
    CaregiverNoteViewSet,
    CognitiveScoreViewSet,
)

router = DefaultRouter()
router.register('exercises', CognitiveExerciseViewSet, basename='cognitive-exercise')
router.register('sessions', ExerciseSessionViewSet, basename='exercise-session')
router.register('assessments', DailyAssessmentViewSet, basename='daily-assessment')
router.register('notes', CaregiverNoteViewSet, basename='caregiver-note')
router.register('scores', CognitiveScoreViewSet, basename='cognitive-score')

urlpatterns = [
    path('', include(router.urls)),
]
