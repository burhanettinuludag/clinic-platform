from django.contrib import admin
from .models import (
    BreathingExercise, RelaxationExercise, ExerciseSession,
    SleepLog, MenstrualLog, WaterIntakeLog, WeatherData, UserWeatherAlert
)


@admin.register(BreathingExercise)
class BreathingExerciseAdmin(admin.ModelAdmin):
    list_display = ['name_tr', 'difficulty', 'cycles', 'is_active', 'order']
    list_filter = ['difficulty', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name_tr', 'name_en']


@admin.register(RelaxationExercise)
class RelaxationExerciseAdmin(admin.ModelAdmin):
    list_display = ['name_tr', 'exercise_type', 'duration_minutes', 'is_active', 'order']
    list_filter = ['exercise_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name_tr', 'name_en']


@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_exercise_name', 'duration_seconds', 'stress_before', 'stress_after', 'completed_at']
    list_filter = ['completed_at']
    search_fields = ['user__email']
    date_hierarchy = 'completed_at'

    def get_exercise_name(self, obj):
        if obj.breathing_exercise:
            return f"Nefes: {obj.breathing_exercise.name_tr}"
        if obj.relaxation_exercise:
            return f"Gevşeme: {obj.relaxation_exercise.name_tr}"
        return "-"
    get_exercise_name.short_description = 'Egzersiz'


@admin.register(SleepLog)
class SleepLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'sleep_duration_minutes', 'sleep_quality', 'had_nightmare']
    list_filter = ['sleep_quality', 'had_nightmare', 'date']
    search_fields = ['user__email']
    date_hierarchy = 'date'


@admin.register(MenstrualLog)
class MenstrualLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'is_period_day', 'flow_intensity', 'has_headache', 'has_cramps']
    list_filter = ['is_period_day', 'flow_intensity', 'has_headache']
    search_fields = ['user__email']
    date_hierarchy = 'date'


@admin.register(WaterIntakeLog)
class WaterIntakeLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'glasses', 'target_glasses']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'humidity', 'pressure', 'weather_condition', 'recorded_at']
    list_filter = ['city', 'weather_condition']
    date_hierarchy = 'recorded_at'


@admin.register(UserWeatherAlert)
class UserWeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'alert_on_pressure_drop', 'is_active']
    list_filter = ['is_active', 'city']
    search_fields = ['user__email']
