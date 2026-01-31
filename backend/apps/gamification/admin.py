from django.contrib import admin
from .models import (
    Badge, UserBadge, UserStreak, UserPoints,
    PointHistory, Achievement, UserAchievement
)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name_tr', 'category', 'rarity', 'points_reward', 'requirement_type', 'requirement_value', 'is_active']
    list_filter = ['category', 'rarity', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name_tr', 'name_en']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge__category', 'earned_at']
    search_fields = ['user__email', 'badge__name_tr']
    date_hierarchy = 'earned_at'


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'streak_type', 'current_streak', 'longest_streak', 'last_activity_date']
    list_filter = ['streak_type']
    search_fields = ['user__email']


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'level', 'points_this_week', 'points_this_month']
    search_fields = ['user__email']
    ordering = ['-total_points']


@admin.register(PointHistory)
class PointHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'reason', 'total_after', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'reason']
    date_hierarchy = 'created_at'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name_tr', 'period', 'target_type', 'target_value', 'points_reward', 'is_active']
    list_filter = ['period', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name_tr', 'name_en']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'current_progress', 'is_completed', 'period_start']
    list_filter = ['is_completed', 'period_start']
    search_fields = ['user__email', 'achievement__name_tr']
