from django.contrib import admin
from .models import DoctorNote


@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'note_type', 'is_private', 'created_at')
    list_filter = ('note_type', 'is_private', 'created_at')
    search_fields = ('doctor__email', 'patient__email', 'content')
    date_hierarchy = 'created_at'
