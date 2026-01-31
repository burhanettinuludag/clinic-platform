from django.contrib import admin
from .models import (
    CognitiveExercise,
    ExerciseSession,
    DailyAssessment,
    CaregiverNote,
    CognitiveScore,
)


@admin.register(CognitiveExercise)
class CognitiveExerciseAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'exercise_type', 'difficulty', 'estimated_duration_minutes', 'is_active', 'order']
    list_filter = ['exercise_type', 'difficulty', 'is_active']
    search_fields = ['name_tr', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['order', 'exercise_type']


@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'exercise', 'started_at', 'score', 'accuracy_percent']
    list_filter = ['exercise__exercise_type', 'started_at']
    search_fields = ['patient__email', 'exercise__name_en']
    date_hierarchy = 'started_at'


@admin.register(DailyAssessment)
class DailyAssessmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessment_date', 'mood_score', 'confusion_level', 'recorded_by']
    list_filter = ['assessment_date', 'fall_occurred', 'wandering_occurred']
    search_fields = ['patient__email']
    date_hierarchy = 'assessment_date'


@admin.register(CaregiverNote)
class CaregiverNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'note_type', 'title', 'severity', 'is_flagged_for_doctor', 'doctor_reviewed', 'created_at']
    list_filter = ['note_type', 'severity', 'is_flagged_for_doctor', 'doctor_reviewed']
    search_fields = ['patient__email', 'title', 'content']
    date_hierarchy = 'created_at'


@admin.register(CognitiveScore)
class CognitiveScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'score_date', 'overall_score', 'memory_score', 'attention_score', 'exercises_completed']
    list_filter = ['score_date']
    search_fields = ['patient__email']
    date_hierarchy = 'score_date'
