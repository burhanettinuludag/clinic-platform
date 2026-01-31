from django.db import models
from django.conf import settings


class BreathingExercise(models.Model):
    """Nefes egzersizleri tanımları"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    ]

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField()
    description_en = models.TextField()

    inhale_seconds = models.PositiveIntegerField(default=4)
    hold_seconds = models.PositiveIntegerField(default=4)
    exhale_seconds = models.PositiveIntegerField(default=4)
    hold_after_exhale_seconds = models.PositiveIntegerField(default=0)

    cycles = models.PositiveIntegerField(default=5)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')

    benefits_tr = models.TextField(blank=True)
    benefits_en = models.TextField(blank=True)

    icon = models.CharField(max_length=50, default='lungs')
    color = models.CharField(max_length=20, default='blue')

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name_tr']

    def __str__(self):
        return self.name_tr


class RelaxationExercise(models.Model):
    """Gevşeme egzersizleri (PMR, body scan, vs.)"""
    TYPE_CHOICES = [
        ('pmr', 'Progresif Kas Gevşetme'),
        ('body_scan', 'Vücut Tarama'),
        ('visualization', 'Görselleştirme'),
        ('grounding', 'Topraklama'),
        ('mindfulness', 'Farkındalık'),
    ]

    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField()
    description_en = models.TextField()

    exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    duration_minutes = models.PositiveIntegerField(default=10)

    steps_tr = models.JSONField(default=list)  # ["Adım 1", "Adım 2", ...]
    steps_en = models.JSONField(default=list)

    audio_url = models.URLField(blank=True, null=True)

    benefits_tr = models.TextField(blank=True)
    benefits_en = models.TextField(blank=True)

    icon = models.CharField(max_length=50, default='spa')
    color = models.CharField(max_length=20, default='purple')

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name_tr']

    def __str__(self):
        return self.name_tr


class ExerciseSession(models.Model):
    """Kullanıcının tamamladığı egzersiz seansları"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    breathing_exercise = models.ForeignKey(
        BreathingExercise, on_delete=models.SET_NULL, null=True, blank=True
    )
    relaxation_exercise = models.ForeignKey(
        RelaxationExercise, on_delete=models.SET_NULL, null=True, blank=True
    )

    duration_seconds = models.PositiveIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    stress_before = models.PositiveIntegerField(null=True, blank=True)  # 1-10
    stress_after = models.PositiveIntegerField(null=True, blank=True)   # 1-10

    notes = models.TextField(blank=True)
    points_earned = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', '-completed_at']),
        ]


class SleepLog(models.Model):
    """Uyku takibi"""
    QUALITY_CHOICES = [
        (1, 'Çok Kötü'),
        (2, 'Kötü'),
        (3, 'Orta'),
        (4, 'İyi'),
        (5, 'Çok İyi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()

    bedtime = models.TimeField()
    wake_time = models.TimeField()

    sleep_duration_minutes = models.PositiveIntegerField()
    sleep_quality = models.PositiveIntegerField(choices=QUALITY_CHOICES)

    had_nightmare = models.BooleanField(default=False)
    woke_up_during_night = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]


class MenstrualLog(models.Model):
    """Adet döngüsü takibi"""
    FLOW_CHOICES = [
        ('spotting', 'Lekelenme'),
        ('light', 'Hafif'),
        ('medium', 'Orta'),
        ('heavy', 'Yoğun'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()

    is_period_day = models.BooleanField(default=True)
    flow_intensity = models.CharField(max_length=20, choices=FLOW_CHOICES, blank=True)

    has_cramps = models.BooleanField(default=False)
    cramp_intensity = models.PositiveIntegerField(null=True, blank=True)  # 1-10

    has_headache = models.BooleanField(default=False)
    has_mood_changes = models.BooleanField(default=False)
    has_bloating = models.BooleanField(default=False)
    has_fatigue = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]


class WaterIntakeLog(models.Model):
    """Su tüketimi takibi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()

    glasses = models.PositiveIntegerField(default=0)  # Her bardak ~250ml
    target_glasses = models.PositiveIntegerField(default=8)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]


class WeatherData(models.Model):
    """Hava durumu verisi (cache için)"""
    city = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5, default='TR')

    temperature = models.FloatField()
    humidity = models.PositiveIntegerField()
    pressure = models.FloatField()  # hPa (millibar)

    weather_condition = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=100)

    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['city', '-recorded_at']),
        ]


class UserWeatherAlert(models.Model):
    """Kullanıcı hava durumu uyarı ayarları"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    city = models.CharField(max_length=100, default='Istanbul')
    country_code = models.CharField(max_length=5, default='TR')

    alert_on_pressure_drop = models.BooleanField(default=True)
    pressure_threshold = models.FloatField(default=5.0)  # hPa drop

    alert_on_humidity_high = models.BooleanField(default=True)
    humidity_threshold = models.PositiveIntegerField(default=80)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
