from rest_framework import serializers
from .models import SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink


class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = [
            'id', 'key', 'label', 'value', 'value_type',
            'description', 'category', 'is_public',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SiteConfigPublicSerializer(serializers.ModelSerializer):
    """Public API - sadece key/value dondurur."""
    typed_value = serializers.SerializerMethodField()

    class Meta:
        model = SiteConfig
        fields = ['key', 'value', 'value_type', 'typed_value']

    def get_typed_value(self, obj):
        return obj.get_typed_value()


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'key', 'label', 'is_enabled',
            'description', 'enabled_for_roles',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureFlagPublicSerializer(serializers.ModelSerializer):
    """Public API - sadece key ve enabled durumu."""
    class Meta:
        model = FeatureFlag
        fields = ['key', 'label', 'is_enabled']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'id', 'title_tr', 'title_en', 'message_tr', 'message_en',
            'link_url', 'link_text_tr', 'link_text_en',
            'bg_color', 'text_color', 'is_active', 'priority',
            'starts_at', 'expires_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HomepageHeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageHero
        fields = [
            'id', 'title_tr', 'title_en', 'subtitle_tr', 'subtitle_en',
            'cta_text_tr', 'cta_text_en', 'cta_url',
            'secondary_cta_text_tr', 'secondary_cta_text_en', 'secondary_cta_url',
            'background_image', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SocialLinkSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = SocialLink
        fields = [
            'id', 'platform', 'platform_display', 'url',
            'is_active', 'order', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
