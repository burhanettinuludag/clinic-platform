from rest_framework import serializers
from .models import (
    BreathingExercise, RelaxationExercise, ExerciseSession,
    SleepLog, MenstrualLog, WaterIntakeLog, WeatherData, UserWeatherAlert
)


class BreathingExerciseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    benefits = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()

    class Meta:
        model = BreathingExercise
        fields = [
            'id', 'name', 'name_tr', 'name_en', 'description', 'description_tr', 'description_en',
            'inhale_seconds', 'hold_seconds', 'exhale_seconds', 'hold_after_exhale_seconds',
            'cycles', 'difficulty', 'benefits', 'benefits_tr', 'benefits_en',
            'icon', 'color', 'total_duration'
        ]

    def get_name(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.name_en if lang == 'en' else obj.name_tr

    def get_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.description_en if lang == 'en' else obj.description_tr

    def get_benefits(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.benefits_en if lang == 'en' else obj.benefits_tr

    def get_total_duration(self, obj):
        cycle_duration = (
            obj.inhale_seconds + obj.hold_seconds +
            obj.exhale_seconds + obj.hold_after_exhale_seconds
        )
        return cycle_duration * obj.cycles


class RelaxationExerciseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    benefits = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()

    class Meta:
        model = RelaxationExercise
        fields = [
            'id', 'name', 'name_tr', 'name_en', 'description', 'description_tr', 'description_en',
            'exercise_type', 'duration_minutes', 'steps', 'steps_tr', 'steps_en',
            'audio_url', 'benefits', 'benefits_tr', 'benefits_en', 'icon', 'color'
        ]

    def get_name(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.name_en if lang == 'en' else obj.name_tr

    def get_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.description_en if lang == 'en' else obj.description_tr

    def get_benefits(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.benefits_en if lang == 'en' else obj.benefits_tr

    def get_steps(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.steps_en if lang == 'en' else obj.steps_tr


class ExerciseSessionSerializer(serializers.ModelSerializer):
    breathing_exercise_name = serializers.CharField(
        source='breathing_exercise.name_tr', read_only=True
    )
    relaxation_exercise_name = serializers.CharField(
        source='relaxation_exercise.name_tr', read_only=True
    )
    stress_reduction = serializers.SerializerMethodField()

    class Meta:
        model = ExerciseSession
        fields = [
            'id', 'breathing_exercise', 'breathing_exercise_name',
            'relaxation_exercise', 'relaxation_exercise_name',
            'duration_seconds', 'completed_at',
            'stress_before', 'stress_after', 'stress_reduction',
            'notes', 'points_earned'
        ]
        read_only_fields = ['completed_at', 'points_earned']

    def get_stress_reduction(self, obj):
        if obj.stress_before and obj.stress_after:
            return obj.stress_before - obj.stress_after
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user

        # Puan hesapla
        duration = validated_data.get('duration_seconds', 0)
        points = max(1, duration // 60)  # Her dakika 1 puan
        validated_data['points_earned'] = points

        return super().create(validated_data)


class SleepLogSerializer(serializers.ModelSerializer):
    sleep_hours = serializers.SerializerMethodField()

    class Meta:
        model = SleepLog
        fields = [
            'id', 'date', 'bedtime', 'wake_time',
            'sleep_duration_minutes', 'sleep_hours', 'sleep_quality',
            'had_nightmare', 'woke_up_during_night', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_sleep_hours(self, obj):
        return round(obj.sleep_duration_minutes / 60, 1)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MenstrualLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenstrualLog
        fields = [
            'id', 'date', 'is_period_day', 'flow_intensity',
            'has_cramps', 'cramp_intensity',
            'has_headache', 'has_mood_changes', 'has_bloating', 'has_fatigue',
            'notes', 'created_at'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WaterIntakeLogSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()
    ml_consumed = serializers.SerializerMethodField()

    class Meta:
        model = WaterIntakeLog
        fields = [
            'id', 'date', 'glasses', 'target_glasses',
            'percentage', 'ml_consumed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_percentage(self, obj):
        if obj.target_glasses > 0:
            return min(100, round((obj.glasses / obj.target_glasses) * 100))
        return 0

    def get_ml_consumed(self, obj):
        return obj.glasses * 250  # Her bardak 250ml

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WeatherDataSerializer(serializers.ModelSerializer):
    pressure_status = serializers.SerializerMethodField()

    class Meta:
        model = WeatherData
        fields = [
            'id', 'city', 'country_code',
            'temperature', 'humidity', 'pressure', 'pressure_status',
            'weather_condition', 'weather_description', 'recorded_at'
        ]

    def get_pressure_status(self, obj):
        if obj.pressure < 1000:
            return 'low'
        elif obj.pressure > 1020:
            return 'high'
        return 'normal'


class UserWeatherAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWeatherAlert
        fields = [
            'id', 'city', 'country_code',
            'alert_on_pressure_drop', 'pressure_threshold',
            'alert_on_humidity_high', 'humidity_threshold',
            'is_active'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
