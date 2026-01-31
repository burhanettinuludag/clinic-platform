from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BadgeViewSet, UserStreakViewSet, UserPointsViewSet,
    AchievementViewSet, GamificationSummaryViewSet
)

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'streaks', UserStreakViewSet, basename='streak')
router.register(r'points', UserPointsViewSet, basename='points')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'summary', GamificationSummaryViewSet, basename='gamification-summary')

urlpatterns = [
    path('', include(router.urls)),
]
