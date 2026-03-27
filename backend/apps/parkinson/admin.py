from django.contrib import admin
from .models import (
    ParkinsonTrigger, ParkinsonSymptomEntry,
    ParkinsonMedication, ParkinsonMedicationSchedule, ParkinsonMedicationLog,
    HoehnYahrAssessment, SchwabEnglandAssessment, NMSQuestAssessment,
    NoseraMotorAssessment, NoseraDailyLivingAssessment,
    ParkinsonVisit,
)


@admin.register(ParkinsonTrigger)
class ParkinsonTriggerAdmin(admin.ModelAdmin):
    list_display = ['name_tr', 'name_en', 'category', 'is_predefined']
    list_filter = ['category', 'is_predefined']
    search_fields = ['name_tr', 'name_en']


@admin.register(ParkinsonSymptomEntry)
class ParkinsonSymptomEntryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_at', 'motor_state', 'overall_severity', 'tremor_severity']
    list_filter = ['motor_state', 'affected_side']
    search_fields = ['patient__email']
    date_hierarchy = 'recorded_at'


class ScheduleInline(admin.TabularInline):
    model = ParkinsonMedicationSchedule
    extra = 1


@admin.register(ParkinsonMedication)
class ParkinsonMedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'patient', 'drug_class', 'dosage_mg', 'frequency_per_day', 'is_active']
    list_filter = ['drug_class', 'is_active']
    search_fields = ['name', 'patient__email']
    inlines = [ScheduleInline]


@admin.register(ParkinsonMedicationLog)
class ParkinsonMedicationLogAdmin(admin.ModelAdmin):
    list_display = ['medication', 'scheduled_time', 'was_taken', 'taken_at']
    list_filter = ['was_taken']
    date_hierarchy = 'scheduled_time'


@admin.register(HoehnYahrAssessment)
class HoehnYahrAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessed_at', 'stage']
    list_filter = ['stage']


@admin.register(SchwabEnglandAssessment)
class SchwabEnglandAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessed_at', 'score']


@admin.register(NMSQuestAssessment)
class NMSQuestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessed_at', 'total_score']


@admin.register(NoseraMotorAssessment)
class NoseraMotorAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessed_at', 'total_score']


@admin.register(NoseraDailyLivingAssessment)
class NoseraDailyLivingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'assessed_at', 'total_score']


@admin.register(ParkinsonVisit)
class ParkinsonVisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'visit_date', 'visit_type', 'doctor_name']
    list_filter = ['visit_type']
    date_hierarchy = 'visit_date'
