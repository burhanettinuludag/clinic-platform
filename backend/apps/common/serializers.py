from rest_framework import serializers
from .models import ConsentRecord


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = [
            'id', 'consent_type', 'version', 'granted',
            'granted_at', 'revoked_at', 'created_at',
        ]
        read_only_fields = ['id', 'granted_at', 'revoked_at', 'created_at']


class GrantConsentSerializer(serializers.Serializer):
    consent_type = serializers.ChoiceField(choices=[
        ('health_data', 'Sağlık Verisi İşleme'),
        ('doctor_sharing', 'Doktor ile Paylaşım'),
        ('marketing', 'Pazarlama İletişimi'),
        ('cookies', 'Çerez Kullanımı'),
    ])
    version = serializers.CharField(max_length=20)
    granted = serializers.BooleanField()
