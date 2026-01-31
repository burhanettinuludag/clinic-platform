from django.contrib import admin
from .models import AuditLog, ConsentRecord


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'ip_address', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('user__email', 'ip_address', 'resource_type')
    readonly_fields = ('user', 'action', 'resource_type', 'ip_address', 'details', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'version', 'granted', 'granted_at', 'revoked_at')
    list_filter = ('consent_type', 'granted', 'version')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)
