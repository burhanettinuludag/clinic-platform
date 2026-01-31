from django.contrib import admin
from .models import SymptomDefinition, SymptomEntry, Medication, MedicationLog, ReminderConfig


@admin.register(SymptomDefinition)
class SymptomDefinitionAdmin(admin.ModelAdmin):
    list_display = ('key', 'label_tr', 'input_type', 'disease_module', 'is_active', 'order')
    list_filter = ('input_type', 'disease_module', 'is_active')
    list_editable = ('is_active', 'order')
    search_fields = ('key', 'label_tr', 'label_en')


@admin.register(SymptomEntry)
class SymptomEntryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'symptom_definition', 'value', 'created_at')
    list_filter = ('symptom_definition', 'created_at')
    search_fields = ('patient__email',)
    date_hierarchy = 'created_at'


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient', 'dosage', 'frequency', 'is_active')
    list_filter = ('is_active', 'frequency')
    search_fields = ('name', 'patient__email')


@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medication', 'was_taken', 'taken_at')
    list_filter = ('was_taken', 'taken_at')
    search_fields = ('patient__email', 'medication__name')
    date_hierarchy = 'taken_at'


@admin.register(ReminderConfig)
class ReminderConfigAdmin(admin.ModelAdmin):
    list_display = ('patient', 'reminder_type', 'time_of_day', 'is_enabled')
    list_filter = ('reminder_type', 'is_enabled')
    search_fields = ('patient__email',)
