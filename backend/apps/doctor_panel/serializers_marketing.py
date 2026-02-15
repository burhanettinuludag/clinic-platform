"""
Marketing Campaign Serializers.
"""

from rest_framework import serializers
from apps.common.models import MarketingCampaign


class MarketingCampaignListSerializer(serializers.ModelSerializer):
    """Kampanya listesi icin ozet serializer."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MarketingCampaign
        fields = [
            'id', 'title', 'theme', 'week_start', 'status', 'status_display',
            'platforms', 'language', 'tone', 'target_audience',
            'total_tokens', 'created_at',
        ]


class MarketingCampaignDetailSerializer(serializers.ModelSerializer):
    """Kampanya detay serializer - tum alanlar."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MarketingCampaign
        fields = [
            'id', 'title', 'theme', 'week_start', 'status', 'status_display',
            'platforms', 'language', 'tone', 'target_audience',
            'content_output', 'visual_briefs', 'schedule',
            'edited_content', 'editor_notes',
            'approved_at', 'total_tokens', 'total_cost_usd',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'content_output', 'visual_briefs', 'schedule',
            'approved_at', 'total_tokens', 'total_cost_usd',
            'created_at', 'updated_at',
        ]


class CreateMarketingCampaignSerializer(serializers.ModelSerializer):
    """Yeni kampanya olusturma serializer."""

    class Meta:
        model = MarketingCampaign
        fields = [
            'theme', 'week_start', 'platforms', 'language',
            'tone', 'target_audience',
        ]

    def validate_theme(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError('Tema en az 5 karakter olmali.')
        return value.strip()

    def create(self, validated_data):
        # Title'i temadan otomatik olustur
        theme = validated_data.get('theme', '')
        validated_data['title'] = theme[:200]
        return super().create(validated_data)


class UpdateMarketingCampaignSerializer(serializers.ModelSerializer):
    """Kampanya duzenleme serializer."""

    class Meta:
        model = MarketingCampaign
        fields = ['edited_content', 'editor_notes', 'status']

    def validate_status(self, value):
        allowed = ['review', 'approved', 'archived']
        if value not in allowed:
            raise serializers.ValidationError(
                f'Gecersiz durum. Izin verilen: {allowed}'
            )
        return value
