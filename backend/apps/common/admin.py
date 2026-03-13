from django.contrib import admin
from .models import (
    AuditLog, ConsentRecord, AgentTask,
    SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink,
    MarketingCampaign, BrokenLink, BrokenLinkScan,
)


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


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'task_type', 'status', 'tokens_used', 'duration_ms', 'created_at']
    list_filter = ['agent_name', 'task_type', 'status']
    readonly_fields = ['input_data', 'output_data']


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'label', 'value', 'category', 'is_public']
    list_filter = ['category', 'is_public', 'value_type']
    list_editable = ['value']
    search_fields = ['key', 'label']


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['key', 'label', 'is_enabled']
    list_editable = ['is_enabled']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title_tr', 'is_active', 'priority', 'starts_at', 'expires_at']
    list_filter = ['is_active']
    list_editable = ['is_active', 'priority']


@admin.register(HomepageHero)
class HomepageHeroAdmin(admin.ModelAdmin):
    list_display = ['title_tr', 'is_active', 'updated_at']
    list_filter = ['is_active']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(BrokenLink)
class BrokenLinkAdmin(admin.ModelAdmin):
    list_display = ['broken_url_short', 'http_status', 'link_type', 'source_type', 'source_title_short', 'status', 'check_count', 'created_at']
    list_filter = ['status', 'link_type', 'source_type', 'http_status']
    search_fields = ['broken_url', 'source_title', 'suggested_url']
    readonly_fields = ['broken_url', 'http_status', 'error_message', 'source_type', 'source_id', 'source_title',
                       'source_field', 'source_language', 'link_type', 'check_count', 'last_checked', 'created_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def broken_url_short(self, obj):
        return obj.broken_url[:80] + '...' if len(obj.broken_url) > 80 else obj.broken_url
    broken_url_short.short_description = 'Kirik URL'

    def source_title_short(self, obj):
        return obj.source_title[:50] + '...' if len(obj.source_title) > 50 else obj.source_title
    source_title_short.short_description = 'Kaynak'


@admin.register(BrokenLinkScan)
class BrokenLinkScanAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'status', 'total_links_checked', 'broken_links_found', 'auto_fixed_count', 'duration_seconds']
    list_filter = ['status']
    readonly_fields = ['status', 'total_links_checked', 'broken_links_found', 'auto_fixed_count',
                       'duration_seconds', 'error_message', 'details', 'created_at']
    ordering = ('-created_at',)


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'theme', 'status', 'week_start', 'total_tokens', 'created_by', 'created_at']
    list_filter = ['status', 'language', 'week_start']
    search_fields = ['title', 'theme']
    readonly_fields = ['content_output', 'visual_briefs', 'schedule', 'total_tokens', 'total_cost_usd', 'pipeline_task']
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
