"""
Social Media API Serializers.
"""

from rest_framework import serializers
from .models import SocialAccount, SocialCampaign, SocialPost, PublishLog


# =============================================================================
# SOCIAL ACCOUNT
# =============================================================================

class SocialAccountListSerializer(serializers.ModelSerializer):
    """List view — token bilgilerini gizle."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_token_valid = serializers.BooleanField(read_only=True)
    connected_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'platform_display', 'account_name', 'account_id',
            'status', 'status_display', 'is_token_valid', 'token_expires_at',
            'page_id', 'organization_urn',
            'total_posts_published', 'followers_count',
            'connected_by', 'connected_by_name',
            'last_used_at', 'created_at',
        ]
        read_only_fields = fields

    def get_connected_by_name(self, obj):
        if obj.connected_by:
            return f"{obj.connected_by.first_name} {obj.connected_by.last_name}".strip()
        return ''


class SocialAccountDetailSerializer(serializers.ModelSerializer):
    """Detail view — token'larin son 4 karakterini goster."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_token_valid = serializers.BooleanField(read_only=True)
    token_hint = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'platform_display', 'account_name', 'account_id',
            'status', 'status_display', 'is_token_valid', 'token_expires_at',
            'token_hint', 'page_id', 'organization_urn',
            'total_posts_published', 'followers_count',
            'connected_by', 'last_used_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_token_hint(self, obj):
        if obj.access_token:
            return f"****{obj.access_token[-4:]}"
        return ''


class CreateSocialAccountSerializer(serializers.ModelSerializer):
    """Yeni hesap baglama."""

    class Meta:
        model = SocialAccount
        fields = [
            'platform', 'account_name', 'account_id',
            'access_token', 'refresh_token', 'token_expires_at',
            'page_id', 'organization_urn',
        ]

    def validate_platform(self, value):
        valid = [c[0] for c in SocialAccount.PLATFORM_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'Gecersiz platform: {value}')
        return value


class UpdateSocialAccountSerializer(serializers.ModelSerializer):
    """Hesap guncelleme (token yenileme vb)."""

    class Meta:
        model = SocialAccount
        fields = [
            'account_name', 'access_token', 'refresh_token',
            'token_expires_at', 'status', 'page_id', 'organization_urn',
        ]


# =============================================================================
# SOCIAL CAMPAIGN
# =============================================================================

class SocialCampaignListSerializer(serializers.ModelSerializer):
    """List view — ozet bilgiler."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    post_stats = serializers.DictField(read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialCampaign
        fields = [
            'id', 'title', 'theme', 'status', 'status_display',
            'platforms', 'posts_per_platform', 'language', 'tone',
            'target_audience', 'week_start',
            'post_stats', 'total_tokens', 'total_cost_usd',
            'created_by', 'created_by_name', 'created_at',
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ''


class SocialCampaignDetailSerializer(serializers.ModelSerializer):
    """Detail view — tum JSON verileri dahil."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    post_stats = serializers.DictField(read_only=True)
    posts = serializers.SerializerMethodField()

    class Meta:
        model = SocialCampaign
        fields = [
            'id', 'title', 'theme', 'description',
            'status', 'status_display',
            'platforms', 'posts_per_platform', 'language', 'tone',
            'target_audience', 'week_start',
            'content_output', 'schedule_output',
            'post_stats', 'posts',
            'total_tokens', 'total_cost_usd',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_posts(self, obj):
        posts = obj.posts.all().order_by('platform', 'scheduled_at')
        return SocialPostListSerializer(posts, many=True).data


class CreateSocialCampaignSerializer(serializers.ModelSerializer):
    """Yeni kampanya olusturma."""

    class Meta:
        model = SocialCampaign
        fields = [
            'title', 'theme', 'description',
            'platforms', 'posts_per_platform',
            'language', 'tone', 'target_audience', 'week_start',
        ]

    def validate_platforms(self, value):
        valid = [c[0] for c in SocialAccount.PLATFORM_CHOICES]
        if not value:
            raise serializers.ValidationError('En az bir platform secilmeli')
        for p in value:
            if p not in valid:
                raise serializers.ValidationError(f'Gecersiz platform: {p}')
        return value

    def validate_posts_per_platform(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('Post sayisi 1-10 arasi olmali')
        return value

    def create(self, validated_data):
        # Baslik yoksa tema'dan olustur
        if not validated_data.get('title'):
            validated_data['title'] = f"Kampanya: {validated_data.get('theme', '')[:50]}"
        return super().create(validated_data)


class UpdateSocialCampaignSerializer(serializers.ModelSerializer):
    """Kampanya guncelleme."""

    class Meta:
        model = SocialCampaign
        fields = [
            'title', 'theme', 'description',
            'platforms', 'posts_per_platform',
            'language', 'tone', 'target_audience', 'week_start',
            'status',
        ]

    def validate_status(self, value):
        valid = [c[0] for c in SocialCampaign.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'Gecersiz status: {value}')
        return value


# =============================================================================
# SOCIAL POST
# =============================================================================

class SocialPostListSerializer(serializers.ModelSerializer):
    """List view — ozet post bilgileri."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_post_format_display', read_only=True)
    final_caption = serializers.CharField(read_only=True)
    campaign_title = serializers.SerializerMethodField()

    class Meta:
        model = SocialPost
        fields = [
            'id', 'platform', 'platform_display',
            'post_format', 'format_display',
            'caption_tr', 'final_caption', 'hashtags',
            'image_urls', 'status', 'status_display',
            'scheduled_at', 'published_at',
            'platform_url', 'publish_error',
            'campaign', 'campaign_title',
            'ai_generated', 'created_at',
        ]
        read_only_fields = fields

    def get_campaign_title(self, obj):
        return obj.campaign.title if obj.campaign else ''


class SocialPostDetailSerializer(serializers.ModelSerializer):
    """Detail view — tum detaylar."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_post_format_display', read_only=True)
    final_caption = serializers.CharField(read_only=True)
    final_caption_with_hashtags = serializers.CharField(read_only=True)
    publish_logs = serializers.SerializerMethodField()
    social_account_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialPost
        fields = [
            'id', 'platform', 'platform_display',
            'post_format', 'format_display',
            'caption_tr', 'caption_en', 'edited_caption',
            'final_caption', 'final_caption_with_hashtags',
            'hashtags', 'image_urls', 'image_prompt', 'visual_brief',
            'scheduled_at', 'published_at',
            'status', 'status_display',
            'social_account', 'social_account_name',
            'platform_post_id', 'platform_url', 'publish_error',
            'editor_notes', 'ai_generated', 'tokens_used',
            'campaign', 'created_by',
            'publish_logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_publish_logs(self, obj):
        logs = obj.publish_logs.all()[:10]
        return PublishLogSerializer(logs, many=True).data

    def get_social_account_name(self, obj):
        if obj.social_account:
            return obj.social_account.account_name
        return ''


class CreateSocialPostSerializer(serializers.ModelSerializer):
    """Yeni post olusturma (manuel)."""

    class Meta:
        model = SocialPost
        fields = [
            'campaign', 'platform', 'post_format',
            'caption_tr', 'caption_en', 'hashtags',
            'image_urls', 'image_prompt', 'visual_brief',
            'scheduled_at', 'social_account',
            'editor_notes',
        ]

    def validate_platform(self, value):
        valid = [c[0] for c in SocialPost.PLATFORM_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'Gecersiz platform: {value}')
        return value


class UpdateSocialPostSerializer(serializers.ModelSerializer):
    """Post guncelleme (duzenleme)."""

    class Meta:
        model = SocialPost
        fields = [
            'edited_caption', 'hashtags', 'image_urls',
            'scheduled_at', 'social_account',
            'editor_notes', 'status',
        ]

    def validate_status(self, value):
        valid = [c[0] for c in SocialPost.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'Gecersiz status: {value}')
        return value


class BulkPostActionSerializer(serializers.Serializer):
    """Toplu post islemi icin serializer."""
    post_ids = serializers.ListField(child=serializers.UUIDField())
    action = serializers.ChoiceField(choices=['approve', 'schedule', 'archive'])
    scheduled_at = serializers.DateTimeField(required=False)
    social_account_id = serializers.UUIDField(required=False)

    def validate(self, data):
        if data['action'] == 'schedule':
            if not data.get('social_account_id'):
                raise serializers.ValidationError('Zamanlama icin sosyal hesap secilmeli')
        return data


# =============================================================================
# PUBLISH LOG
# =============================================================================

class PublishLogSerializer(serializers.ModelSerializer):
    """Yayinlama log serializer."""

    class Meta:
        model = PublishLog
        fields = ['id', 'action', 'success', 'response_data', 'error_message', 'created_at']
        read_only_fields = fields


# =============================================================================
# DASHBOARD STATS
# =============================================================================

class SocialDashboardStatsSerializer(serializers.Serializer):
    """Dashboard istatistikleri."""
    total_accounts = serializers.IntegerField()
    active_accounts = serializers.IntegerField()
    expired_accounts = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    scheduled_posts = serializers.IntegerField()
    failed_posts = serializers.IntegerField()
    posts_by_platform = serializers.DictField()
    total_tokens_used = serializers.IntegerField()


# =============================================================================
# CALENDAR
# =============================================================================

class CalendarPostSerializer(serializers.ModelSerializer):
    """Takvim goruntuleme icin minimal post bilgileri."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SocialPost
        fields = [
            'id', 'platform', 'platform_display',
            'caption_tr', 'status', 'status_display',
            'scheduled_at', 'published_at',
            'post_format', 'campaign',
        ]
        read_only_fields = fields
