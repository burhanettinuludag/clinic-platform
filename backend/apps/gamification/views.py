from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, date

from .models import (
    Badge, UserBadge, UserStreak, UserPoints,
    PointHistory, Achievement, UserAchievement
)
from .serializers import (
    BadgeSerializer, UserBadgeSerializer, UserStreakSerializer,
    UserPointsSerializer, PointHistorySerializer,
    AchievementSerializer, UserAchievementSerializer
)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """Tüm rozetler"""
    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_badges(self, request):
        """Kullanıcının kazandığı rozetler"""
        user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')
        return Response(UserBadgeSerializer(user_badges, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Henüz kazanılmamış rozetler"""
        earned_badge_ids = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)
        available = Badge.objects.filter(is_active=True).exclude(id__in=earned_badge_ids)
        return Response(BadgeSerializer(available, many=True, context={'request': request}).data)


class UserStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanıcı serileri"""
    serializer_class = UserStreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserStreak.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Tüm serilerin özeti"""
        streaks = self.get_queryset()
        summary = {
            'streaks': UserStreakSerializer(streaks, many=True).data,
            'total_active_streaks': streaks.filter(
                last_activity_date=date.today()
            ).count(),
            'longest_overall': max(
                [s.longest_streak for s in streaks], default=0
            ),
        }
        return Response(summary)


class UserPointsViewSet(viewsets.ViewSet):
    """Kullanıcı puanları"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Puan bilgisi"""
        points, _ = UserPoints.objects.get_or_create(user=request.user)
        return Response(UserPointsSerializer(points).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Puan geçmişi"""
        history = PointHistory.objects.filter(user=request.user)[:50]
        return Response(PointHistorySerializer(history, many=True).data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Haftalık liderlik tablosu"""
        top_users = UserPoints.objects.order_by('-points_this_week')[:10]
        leaderboard = []
        for i, up in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': up.user.id,
                'name': f"{up.user.first_name} {up.user.last_name[:1]}.",
                'points': up.points_this_week,
                'level': up.level,
            })
        return Response(leaderboard)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Başarımlar"""
    queryset = Achievement.objects.filter(is_active=True)
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Kullanıcının başarım ilerlemesi"""
        user_achievements = UserAchievement.objects.filter(
            user=request.user
        ).select_related('achievement')

        # Aktif ve tamamlanmış olarak ayır
        active = user_achievements.filter(is_completed=False)
        completed = user_achievements.filter(is_completed=True)

        return Response({
            'active': UserAchievementSerializer(active, many=True, context={'request': request}).data,
            'completed': UserAchievementSerializer(completed, many=True, context={'request': request}).data,
            'total_completed': completed.count(),
        })

    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Günlük hedefler"""
        today = date.today()
        daily_achievements = Achievement.objects.filter(
            is_active=True, period='daily'
        )

        result = []
        for achievement in daily_achievements:
            user_progress, _ = UserAchievement.objects.get_or_create(
                user=request.user,
                achievement=achievement,
                period_start=today,
                defaults={'current_progress': 0}
            )
            result.append(
                UserAchievementSerializer(user_progress, context={'request': request}).data
            )

        return Response(result)


class GamificationSummaryViewSet(viewsets.ViewSet):
    """Genel gamification özeti"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Tam özet"""
        user = request.user

        # Puanlar
        points, _ = UserPoints.objects.get_or_create(user=user)

        # Seriler
        streaks = UserStreak.objects.filter(user=user)

        # Son kazanılan rozetler
        recent_badges = UserBadge.objects.filter(user=user).order_by('-earned_at')[:5]

        # Aktif başarımlar
        active_achievements = UserAchievement.objects.filter(
            user=user, is_completed=False
        ).select_related('achievement')[:5]

        summary = {
            'points': UserPointsSerializer(points).data,
            'streaks': UserStreakSerializer(streaks, many=True).data,
            'recent_badges': UserBadgeSerializer(recent_badges, many=True, context={'request': request}).data,
            'active_achievements': UserAchievementSerializer(
                active_achievements, many=True, context={'request': request}
            ).data,
            'stats': {
                'total_badges': UserBadge.objects.filter(user=user).count(),
                'active_streaks': streaks.filter(last_activity_date=date.today()).count(),
                'completed_achievements': UserAchievement.objects.filter(
                    user=user, is_completed=True
                ).count(),
            }
        }

        return Response(summary)
