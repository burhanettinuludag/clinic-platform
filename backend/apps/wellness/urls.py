from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BreathingExerciseViewSet, RelaxationExerciseViewSet, ExerciseSessionViewSet,
    SleepLogViewSet, MenstrualLogViewSet, WaterIntakeLogViewSet,
    WeatherViewSet, UserWeatherAlertViewSet
)

router = DefaultRouter()
router.register(r'breathing', BreathingExerciseViewSet, basename='breathing')
router.register(r'relaxation', RelaxationExerciseViewSet, basename='relaxation')
router.register(r'sessions', ExerciseSessionViewSet, basename='exercise-session')
router.register(r'sleep', SleepLogViewSet, basename='sleep')
router.register(r'menstrual', MenstrualLogViewSet, basename='menstrual')
router.register(r'water', WaterIntakeLogViewSet, basename='water')
router.register(r'weather', WeatherViewSet, basename='weather')
router.register(r'weather-alerts', UserWeatherAlertViewSet, basename='weather-alert')

urlpatterns = [
    path('', include(router.urls)),
]
