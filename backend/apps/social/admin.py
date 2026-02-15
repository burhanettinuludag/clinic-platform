"""
Social Media Admin registrations.
"""

from django.contrib import admin
from .models import SocialAccount, SocialCampaign, SocialPost, PublishLog


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('platform', 'account_name', 'status', 'connected_by', 'total_posts_published', 'created_at')
    list_filter = ('platform', 'status')
    search_fields = ('account_name', 'account_id')
    readonly_fields = ('access_token', 'refresh_token', 'created_at', 'updated_at')


@admin.register(SocialCampaign)
class SocialCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'status', 'week_start', 'total_tokens', 'created_by', 'created_at')
    list_filter = ('status', 'language', 'platforms')
    search_fields = ('title', 'theme')
    readonly_fields = ('content_output', 'schedule_output', 'total_tokens', 'total_cost_usd', 'created_at', 'updated_at')


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'platform', 'post_format', 'status', 'campaign', 'scheduled_at', 'published_at')
    list_filter = ('platform', 'status', 'post_format', 'ai_generated')
    search_fields = ('caption_tr', 'caption_en')
    readonly_fields = ('platform_post_id', 'platform_url', 'publish_error', 'created_at', 'updated_at')
    raw_id_fields = ('campaign', 'social_account', 'created_by')


@admin.register(PublishLog)
class PublishLogAdmin(admin.ModelAdmin):
    list_display = ('post', 'action', 'success', 'created_at')
    list_filter = ('success', 'action')
    readonly_fields = ('response_data', 'created_at', 'updated_at')
    raw_id_fields = ('post',)
