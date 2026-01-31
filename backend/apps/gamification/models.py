from django.db import models
from django.conf import settings


class Badge(models.Model):
    """Rozet tanımları"""
    CATEGORY_CHOICES = [
        ('tracking', 'Takip'),
        ('streak', 'Seri'),
        ('milestone', 'Kilometre Taşı'),
        ('wellness', 'Sağlık'),
        ('social', 'Sosyal'),
    ]

    RARITY_CHOICES = [
        ('common', 'Yaygın'),
        ('uncommon', 'Nadir'),
        ('rare', 'Çok Nadir'),
        ('epic', 'Epik'),
        ('legendary', 'Efsanevi'),
    ]

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField()
    description_en = models.TextField()

    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='gold')

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')

    points_reward = models.PositiveIntegerField(default=10)

    requirement_type = models.CharField(max_length=50)  # 'streak_days', 'total_attacks_logged', etc.
    requirement_value = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'requirement_value']

    def __str__(self):
        return self.name_tr


class UserBadge(models.Model):
    """Kullanıcının kazandığı rozetler"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']


class UserStreak(models.Model):
    """Kullanıcı seri takibi"""
    STREAK_TYPE_CHOICES = [
        ('daily_log', 'Günlük Kayıt'),
        ('migraine_diary', 'Migren Günlüğü'),
        ('water_intake', 'Su Tüketimi'),
        ('sleep_log', 'Uyku Kaydı'),
        ('exercise', 'Egzersiz'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    streak_type = models.CharField(max_length=30, choices=STREAK_TYPE_CHOICES)

    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)

    last_activity_date = models.DateField(null=True, blank=True)
    streak_started_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'streak_type']

    def update_streak(self, activity_date):
        from datetime import timedelta

        if self.last_activity_date is None:
            self.current_streak = 1
            self.streak_started_at = activity_date
        elif activity_date == self.last_activity_date:
            pass  # Aynı gün, değişiklik yok
        elif activity_date == self.last_activity_date + timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1
            self.streak_started_at = activity_date

        self.last_activity_date = activity_date
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.save()
        return self.current_streak


class UserPoints(models.Model):
    """Kullanıcı puan sistemi"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    points_this_week = models.PositiveIntegerField(default=0)
    points_this_month = models.PositiveIntegerField(default=0)

    last_points_reset = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_points(self, points, reason=''):
        self.total_points += points
        self.points_this_week += points
        self.points_this_month += points

        # Level hesaplama (her 100 puan = 1 level)
        self.level = (self.total_points // 100) + 1

        self.save()

        # Puan geçmişi kaydet
        PointHistory.objects.create(
            user=self.user,
            points=points,
            reason=reason,
            total_after=self.total_points
        )

        return self.total_points

    @property
    def points_to_next_level(self):
        return (self.level * 100) - self.total_points


class PointHistory(models.Model):
    """Puan geçmişi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    points = models.IntegerField()  # Negatif olabilir (harcama için)
    reason = models.CharField(max_length=200)
    total_after = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Achievement(models.Model):
    """Başarım/hedef tanımları"""
    PERIOD_CHOICES = [
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('one_time', 'Tek Seferlik'),
    ]

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField()
    description_en = models.TextField()

    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='blue')

    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    target_type = models.CharField(max_length=50)  # 'log_migraine', 'drink_water', etc.
    target_value = models.PositiveIntegerField()

    points_reward = models.PositiveIntegerField(default=5)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['period', 'name_tr']

    def __str__(self):
        return self.name_tr


class UserAchievement(models.Model):
    """Kullanıcının başarım ilerlemesi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)

    current_progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    period_start = models.DateField()  # Haftalık/aylık hedefler için
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
