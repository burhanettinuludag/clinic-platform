"""
Unit tests for gamification models.
"""

import pytest
from datetime import date, timedelta
from apps.gamification.models import (
    Badge,
    UserBadge,
    UserStreak,
    UserPoints,
    PointHistory,
    Achievement,
    UserAchievement,
)


@pytest.mark.django_db
class TestBadge:
    """Tests for Badge model."""

    def test_create_badge(self, db):
        """Test creating a badge."""
        badge = Badge.objects.create(
            name_tr='Ilk Adim',
            name_en='First Step',
            description_tr='Ilk migren kaydini yaptiniz',
            description_en='You logged your first migraine',
            icon='trophy',
            color='gold',
            category='milestone',
            rarity='common',
            points_reward=10,
            requirement_type='total_attacks_logged',
            requirement_value=1,
        )
        assert badge.name_en == 'First Step'
        assert badge.category == 'milestone'
        assert badge.rarity == 'common'
        assert badge.points_reward == 10

    def test_badge_str(self, db):
        """Test badge string representation."""
        badge = Badge.objects.create(
            name_tr='Test Rozet',
            name_en='Test Badge',
            description_tr='Test',
            description_en='Test',
            icon='star',
            category='tracking',
            requirement_type='test',
            requirement_value=1,
        )
        assert str(badge) == 'Test Rozet'

    def test_badge_categories(self, db):
        """Test all badge category choices."""
        categories = ['tracking', 'streak', 'milestone', 'wellness', 'social']
        for cat in categories:
            badge = Badge.objects.create(
                name_tr=f'Test {cat}',
                name_en=f'Test {cat}',
                description_tr='Test',
                description_en='Test',
                icon='star',
                category=cat,
                requirement_type='test',
                requirement_value=1,
            )
            assert badge.category == cat

    def test_badge_rarities(self, db):
        """Test all badge rarity choices."""
        rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        for rarity in rarities:
            badge = Badge.objects.create(
                name_tr=f'Test {rarity}',
                name_en=f'Test {rarity}',
                description_tr='Test',
                description_en='Test',
                icon='star',
                category='tracking',
                rarity=rarity,
                requirement_type='test',
                requirement_value=1,
            )
            assert badge.rarity == rarity


@pytest.mark.django_db
class TestUserBadge:
    """Tests for UserBadge model."""

    @pytest.fixture
    def badge(self, db):
        """Create a badge for testing."""
        return Badge.objects.create(
            name_tr='Test Rozet',
            name_en='Test Badge',
            description_tr='Test',
            description_en='Test',
            icon='star',
            category='tracking',
            requirement_type='test',
            requirement_value=1,
        )

    def test_earn_badge(self, patient_user, badge):
        """Test user earning a badge."""
        user_badge = UserBadge.objects.create(
            user=patient_user,
            badge=badge,
        )
        assert user_badge.user == patient_user
        assert user_badge.badge == badge
        assert user_badge.earned_at is not None

    def test_unique_badge_per_user(self, patient_user, badge):
        """Test user can only earn each badge once."""
        UserBadge.objects.create(user=patient_user, badge=badge)
        with pytest.raises(Exception):
            UserBadge.objects.create(user=patient_user, badge=badge)


@pytest.mark.django_db
class TestUserStreak:
    """Tests for UserStreak model."""

    def test_create_streak(self, patient_user):
        """Test creating a user streak."""
        streak = UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
            current_streak=5,
            longest_streak=10,
            last_activity_date=date.today(),
        )
        assert streak.streak_type == 'daily_log'
        assert streak.current_streak == 5
        assert streak.longest_streak == 10

    def test_streak_types(self, patient_user):
        """Test all streak type choices."""
        types = ['daily_log', 'migraine_diary', 'water_intake', 'sleep_log', 'exercise']
        for streak_type in types:
            streak = UserStreak.objects.create(
                user=patient_user,
                streak_type=streak_type,
            )
            assert streak.streak_type == streak_type

    def test_update_streak_first_activity(self, patient_user):
        """Test updating streak on first activity."""
        streak = UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
        )
        today = date.today()
        result = streak.update_streak(today)
        assert result == 1
        assert streak.current_streak == 1
        assert streak.longest_streak == 1
        assert streak.streak_started_at == today

    def test_update_streak_consecutive_day(self, patient_user):
        """Test updating streak on consecutive day."""
        yesterday = date.today() - timedelta(days=1)
        streak = UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
            current_streak=5,
            longest_streak=5,
            last_activity_date=yesterday,
            streak_started_at=yesterday - timedelta(days=4),
        )
        today = date.today()
        result = streak.update_streak(today)
        assert result == 6
        assert streak.current_streak == 6
        assert streak.longest_streak == 6

    def test_update_streak_same_day(self, patient_user):
        """Test updating streak on same day doesn't change anything."""
        today = date.today()
        streak = UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
            current_streak=5,
            longest_streak=5,
            last_activity_date=today,
        )
        result = streak.update_streak(today)
        assert result == 5
        assert streak.current_streak == 5

    def test_update_streak_broken(self, patient_user):
        """Test streak resets when broken."""
        two_days_ago = date.today() - timedelta(days=2)
        streak = UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
            current_streak=10,
            longest_streak=10,
            last_activity_date=two_days_ago,
        )
        today = date.today()
        result = streak.update_streak(today)
        assert result == 1
        assert streak.current_streak == 1
        assert streak.longest_streak == 10  # Longest streak preserved

    def test_unique_streak_type_per_user(self, patient_user):
        """Test only one streak per type per user."""
        UserStreak.objects.create(
            user=patient_user,
            streak_type='daily_log',
        )
        with pytest.raises(Exception):
            UserStreak.objects.create(
                user=patient_user,
                streak_type='daily_log',
            )


@pytest.mark.django_db
class TestUserPoints:
    """Tests for UserPoints model."""

    def test_create_user_points(self, patient_user):
        """Test creating user points."""
        points = UserPoints.objects.create(
            user=patient_user,
            total_points=150,
            level=2,
        )
        assert points.total_points == 150
        assert points.level == 2

    def test_add_points(self, patient_user):
        """Test adding points to user."""
        points = UserPoints.objects.create(user=patient_user)
        result = points.add_points(50, 'Logged migraine attack')
        assert result == 50
        assert points.total_points == 50
        assert points.points_this_week == 50
        assert points.points_this_month == 50

    def test_level_calculation(self, patient_user):
        """Test level is calculated correctly."""
        points = UserPoints.objects.create(user=patient_user)
        points.add_points(250, 'Test')
        assert points.level == 3  # (250 // 100) + 1 = 3

    def test_points_to_next_level(self, patient_user):
        """Test points_to_next_level property."""
        points = UserPoints.objects.create(
            user=patient_user,
            total_points=150,
            level=2,
        )
        assert points.points_to_next_level == 50  # (2 * 100) - 150 = 50

    def test_point_history_created(self, patient_user):
        """Test point history is created when adding points."""
        points = UserPoints.objects.create(user=patient_user)
        points.add_points(25, 'Completed exercise')
        history = PointHistory.objects.filter(user=patient_user).first()
        assert history is not None
        assert history.points == 25
        assert history.reason == 'Completed exercise'
        assert history.total_after == 25

    def test_one_points_record_per_user(self, patient_user):
        """Test only one points record per user."""
        UserPoints.objects.create(user=patient_user)
        with pytest.raises(Exception):
            UserPoints.objects.create(user=patient_user)


@pytest.mark.django_db
class TestPointHistory:
    """Tests for PointHistory model."""

    def test_create_point_history(self, patient_user):
        """Test creating point history."""
        history = PointHistory.objects.create(
            user=patient_user,
            points=10,
            reason='Daily login bonus',
            total_after=110,
        )
        assert history.points == 10
        assert history.reason == 'Daily login bonus'

    def test_negative_points(self, patient_user):
        """Test point history can have negative points."""
        history = PointHistory.objects.create(
            user=patient_user,
            points=-50,
            reason='Purchased item',
            total_after=50,
        )
        assert history.points == -50

    def test_history_ordering(self, patient_user):
        """Test history is ordered by created_at descending."""
        h1 = PointHistory.objects.create(
            user=patient_user, points=10, reason='First', total_after=10,
        )
        h2 = PointHistory.objects.create(
            user=patient_user, points=20, reason='Second', total_after=30,
        )
        history = list(PointHistory.objects.filter(user=patient_user))
        assert history[0] == h2
        assert history[1] == h1


@pytest.mark.django_db
class TestAchievement:
    """Tests for Achievement model."""

    def test_create_achievement(self, db):
        """Test creating an achievement."""
        achievement = Achievement.objects.create(
            name_tr='Su Icme Ustasi',
            name_en='Water Drinking Master',
            description_tr='8 bardak su ic',
            description_en='Drink 8 glasses of water',
            icon='droplet',
            color='blue',
            period='daily',
            target_type='drink_water',
            target_value=8,
            points_reward=15,
        )
        assert achievement.period == 'daily'
        assert achievement.target_value == 8
        assert achievement.points_reward == 15

    def test_achievement_str(self, db):
        """Test achievement string representation."""
        achievement = Achievement.objects.create(
            name_tr='Test Basarim',
            name_en='Test Achievement',
            description_tr='Test',
            description_en='Test',
            icon='star',
            period='daily',
            target_type='test',
            target_value=1,
        )
        assert str(achievement) == 'Test Basarim'

    def test_achievement_periods(self, db):
        """Test all achievement period choices."""
        periods = ['daily', 'weekly', 'monthly', 'one_time']
        for period in periods:
            achievement = Achievement.objects.create(
                name_tr=f'Test {period}',
                name_en=f'Test {period}',
                description_tr='Test',
                description_en='Test',
                icon='star',
                period=period,
                target_type='test',
                target_value=1,
            )
            assert achievement.period == period


@pytest.mark.django_db
class TestUserAchievement:
    """Tests for UserAchievement model."""

    @pytest.fixture
    def achievement(self, db):
        """Create an achievement for testing."""
        return Achievement.objects.create(
            name_tr='Test Basarim',
            name_en='Test Achievement',
            description_tr='Test',
            description_en='Test',
            icon='star',
            period='daily',
            target_type='test',
            target_value=5,
        )

    def test_create_user_achievement(self, patient_user, achievement):
        """Test creating user achievement progress."""
        user_achievement = UserAchievement.objects.create(
            user=patient_user,
            achievement=achievement,
            current_progress=3,
            is_completed=False,
            period_start=date.today(),
        )
        assert user_achievement.current_progress == 3
        assert user_achievement.is_completed is False

    def test_completed_achievement(self, patient_user, achievement):
        """Test marking achievement as completed."""
        from django.utils import timezone
        now = timezone.now()
        user_achievement = UserAchievement.objects.create(
            user=patient_user,
            achievement=achievement,
            current_progress=5,
            is_completed=True,
            completed_at=now,
            period_start=date.today(),
        )
        assert user_achievement.is_completed is True
        assert user_achievement.completed_at is not None
