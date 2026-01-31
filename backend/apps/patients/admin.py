from django.contrib import admin
from .models import DiseaseModule, PatientModule, TaskTemplate, TaskCompletion


@admin.register(DiseaseModule)
class DiseaseModuleAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'disease_type', 'is_active', 'order')
    list_filter = ('disease_type', 'is_active')
    list_editable = ('is_active', 'order')
    search_fields = ('name_tr', 'name_en')


@admin.register(PatientModule)
class PatientModuleAdmin(admin.ModelAdmin):
    list_display = ('patient', 'disease_module', 'is_active', 'enrolled_at')
    list_filter = ('is_active', 'disease_module')
    search_fields = ('patient__email', 'patient__first_name')


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'disease_module', 'task_type', 'frequency', 'points', 'is_active')
    list_filter = ('task_type', 'frequency', 'disease_module', 'is_active')
    list_editable = ('points', 'is_active')
    search_fields = ('title_tr', 'title_en')


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'task_template', 'completed_date')
    list_filter = ('completed_date',)
    search_fields = ('patient__email',)
    date_hierarchy = 'completed_date'
