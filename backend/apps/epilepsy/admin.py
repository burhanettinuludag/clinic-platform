from django.contrib import admin
from .models import SeizureEvent, EpilepsyTrigger


@admin.register(SeizureEvent)
class SeizureEventAdmin(admin.ModelAdmin):
    list_display = ('patient', 'seizure_type', 'intensity', 'duration_seconds', 'medication_taken', 'seizure_datetime')
    list_filter = ('seizure_type', 'loss_of_consciousness', 'medication_taken', 'seizure_datetime')
    search_fields = ('patient__email', 'patient__first_name')
    date_hierarchy = 'seizure_datetime'


@admin.register(EpilepsyTrigger)
class EpilepsyTriggerAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'category', 'is_predefined')
    list_filter = ('category', 'is_predefined')
    search_fields = ('name_tr', 'name_en')
