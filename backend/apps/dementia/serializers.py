from rest_framework import serializers
from .models import (
    CognitiveExercise,
    ExerciseSession,
    DailyAssessment,
    CaregiverNote,
    CognitiveScore,
    CognitiveScreening,
)


class CognitiveExerciseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    instructions = serializers.SerializerMethodField()
    exercise_type_display = serializers.CharField(source='get_exercise_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = CognitiveExercise
        fields = [
            'id', 'slug', 'name', 'name_tr', 'name_en',
            'description', 'description_tr', 'description_en',
            'instructions', 'instructions_tr', 'instructions_en',
            'exercise_type', 'exercise_type_display',
            'difficulty', 'difficulty_display',
            'estimated_duration_minutes', 'icon', 'config', 'order',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)

    def get_instructions(self, obj):
        return getattr(obj, f'instructions_{self._get_lang()}', obj.instructions_tr)


class ExerciseSessionSerializer(serializers.ModelSerializer):
    exercise_name = serializers.SerializerMethodField()
    exercise_type = serializers.CharField(source='exercise.exercise_type', read_only=True)

    class Meta:
        model = ExerciseSession
        fields = [
            'id', 'exercise', 'exercise_name', 'exercise_type',
            'started_at', 'completed_at', 'duration_seconds',
            'score', 'max_possible_score', 'accuracy_percent',
            'results_data', 'difficulty_rating', 'notes',
        ]
        read_only_fields = ['started_at']

    def get_exercise_name(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            lang = request.headers.get('Accept-Language', 'tr')[:2]
        else:
            lang = 'tr'
        return getattr(obj.exercise, f'name_{lang}', obj.exercise.name_tr)


class ExerciseSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseSession
        fields = [
            'exercise', 'completed_at', 'duration_seconds',
            'score', 'max_possible_score', 'accuracy_percent',
            'results_data', 'difficulty_rating', 'notes',
        ]


class DailyAssessmentSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)

    class Meta:
        model = DailyAssessment
        fields = [
            'id', 'assessment_date', 'recorded_by', 'recorded_by_name',
            # Mood and Mental State
            'mood_score', 'confusion_level', 'agitation_level', 'anxiety_level',
            # Sleep
            'sleep_quality', 'sleep_hours', 'night_wandering',
            # ADL
            'eating_independence', 'dressing_independence',
            'hygiene_independence', 'mobility_independence',
            # Communication
            'verbal_communication', 'recognition_family',
            # Incidents
            'fall_occurred', 'wandering_occurred', 'medication_missed',
            # Notes
            'notes', 'concerns',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['recorded_by', 'created_at', 'updated_at']


class CaregiverNoteSerializer(serializers.ModelSerializer):
    caregiver_name = serializers.CharField(source='caregiver.get_full_name', read_only=True)
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)

    class Meta:
        model = CaregiverNote
        fields = [
            'id', 'patient', 'caregiver', 'caregiver_name',
            'note_type', 'note_type_display',
            'title', 'content', 'severity',
            'is_flagged_for_doctor', 'doctor_reviewed', 'doctor_reviewed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['caregiver', 'doctor_reviewed', 'doctor_reviewed_at', 'created_at', 'updated_at']


class CognitiveScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveScore
        fields = [
            'id', 'score_date',
            'memory_score', 'attention_score', 'language_score',
            'problem_solving_score', 'orientation_score', 'overall_score',
            'exercises_completed', 'total_exercise_minutes',
        ]


class CognitiveStatsSerializer(serializers.Serializer):
    """Statistics for dementia patient dashboard."""
    total_exercises_completed = serializers.IntegerField()
    exercises_this_week = serializers.IntegerField()
    current_streak_days = serializers.IntegerField()
    avg_score_this_week = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    avg_score_last_week = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    score_trend = serializers.CharField()  # 'improving', 'stable', 'declining'
    favorite_exercise_type = serializers.CharField(allow_null=True)
    last_assessment_date = serializers.DateField(allow_null=True)


class CognitiveScreeningSerializer(serializers.ModelSerializer):
    interpretation = serializers.SerializerMethodField()
    interpretation_label = serializers.SerializerMethodField()
    domain_scores = serializers.SerializerMethodField()
    administered_by_name = serializers.CharField(source='administered_by.get_full_name', read_only=True)

    class Meta:
        model = CognitiveScreening
        fields = [
            'id', 'assessment_date', 'administered_by', 'administered_by_name',
            'orientation_score', 'memory_score', 'attention_score',
            'language_score', 'executive_score', 'total_score',
            'responses', 'duration_minutes', 'notes',
            'interpretation', 'interpretation_label', 'domain_scores',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['total_score', 'created_at', 'updated_at']

    def get_interpretation(self, obj):
        code, _ = obj.get_interpretation()
        return code

    def get_interpretation_label(self, obj):
        _, label = obj.get_interpretation()
        return label

    def get_domain_scores(self, obj):
        return obj.get_domain_scores()


class CognitiveScreeningCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveScreening
        fields = [
            'assessment_date',
            'orientation_score', 'memory_score', 'attention_score',
            'language_score', 'executive_score',
            'responses', 'duration_minutes', 'notes',
        ]
