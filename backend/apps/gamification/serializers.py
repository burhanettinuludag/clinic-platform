from rest_framework import serializers
from .models import (
    Badge, UserBadge, UserStreak, UserPoints,
    PointHistory, Achievement, UserAchievement
)


class BadgeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'name_tr', 'name_en',
            'description', 'description_tr', 'description_en',
            'icon', 'color', 'category', 'rarity', 'points_reward',
            'requirement_type', 'requirement_value'
        ]

    def get_name(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.name_en if lang == 'en' else obj.name_tr

    def get_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.description_en if lang == 'en' else obj.description_tr


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']


class UserStreakSerializer(serializers.ModelSerializer):
    streak_type_display = serializers.CharField(
        source='get_streak_type_display', read_only=True
    )
    is_active_today = serializers.SerializerMethodField()

    class Meta:
        model = UserStreak
        fields = [
            'id', 'streak_type', 'streak_type_display',
            'current_streak', 'longest_streak',
            'last_activity_date', 'streak_started_at',
            'is_active_today'
        ]

    def get_is_active_today(self, obj):
        from datetime import date
        return obj.last_activity_date == date.today()


class UserPointsSerializer(serializers.ModelSerializer):
    points_to_next_level = serializers.IntegerField(read_only=True)
    level_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserPoints
        fields = [
            'total_points', 'level', 'points_to_next_level', 'level_progress',
            'points_this_week', 'points_this_month'
        ]

    def get_level_progress(self, obj):
        points_in_level = obj.total_points % 100
        return points_in_level


class PointHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PointHistory
        fields = ['id', 'points', 'reason', 'total_after', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'name_tr', 'name_en',
            'description', 'description_tr', 'description_en',
            'icon', 'color', 'period', 'target_type', 'target_value',
            'points_reward'
        ]

    def get_name(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.name_en if lang == 'en' else obj.name_tr

    def get_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.description_en if lang == 'en' else obj.description_tr


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'current_progress',
            'is_completed', 'completed_at',
            'progress_percentage', 'period_start'
        ]

    def get_progress_percentage(self, obj):
        if obj.achievement.target_value > 0:
            return min(100, round(
                (obj.current_progress / obj.achievement.target_value) * 100
            ))
        return 0


class GamificationSummarySerializer(serializers.Serializer):
    """Kullanıcının genel gamification özeti"""
    points = UserPointsSerializer()
    streaks = UserStreakSerializer(many=True)
    recent_badges = UserBadgeSerializer(many=True)
    active_achievements = UserAchievementSerializer(many=True)
