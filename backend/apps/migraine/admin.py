from django.contrib import admin
from .models import MigraineAttack, MigraineTrigger


@admin.register(MigraineAttack)
class MigraineAttackAdmin(admin.ModelAdmin):
    list_display = ('patient', 'intensity', 'duration_minutes', 'pain_location', 'has_aura', 'start_datetime')
    list_filter = ('pain_location', 'has_aura', 'start_datetime')
    search_fields = ('patient__email', 'patient__first_name')
    date_hierarchy = 'start_datetime'


@admin.register(MigraineTrigger)
class MigraineTriggerAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'category', 'is_predefined')
    list_filter = ('category', 'is_predefined')
    search_fields = ('name_tr', 'name_en')
