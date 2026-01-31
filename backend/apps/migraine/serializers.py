from rest_framework import serializers
from .models import MigraineAttack, MigraineTrigger


class MigraineTriggerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = MigraineTrigger
        fields = ['id', 'name', 'name_tr', 'name_en', 'category', 'is_predefined', 'created_by']
        read_only_fields = ['created_by']

    def get_name(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            lang = request.headers.get('Accept-Language', 'tr')[:2]
        else:
            lang = 'tr'
        return getattr(obj, f'name_{lang}', obj.name_tr)


class MigraineAttackSerializer(serializers.ModelSerializer):
    triggers_identified = MigraineTriggerSerializer(many=True, read_only=True)
    trigger_ids = serializers.PrimaryKeyRelatedField(
        queryset=MigraineTrigger.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='triggers_identified',
    )

    class Meta:
        model = MigraineAttack
        fields = [
            'id', 'start_datetime', 'end_datetime', 'duration_minutes',
            'intensity', 'pain_location',
            'has_aura', 'has_nausea', 'has_vomiting',
            'has_photophobia', 'has_phonophobia',
            'medication_taken', 'medication_effective',
            'triggers_identified', 'trigger_ids',
            'notes', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_intensity(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Intensity must be between 1 and 10.")
        return value

    def create(self, validated_data):
        triggers = validated_data.pop('triggers_identified', [])
        attack = MigraineAttack.objects.create(**validated_data)
        if triggers:
            attack.triggers_identified.set(triggers)
        return attack

    def update(self, instance, validated_data):
        triggers = validated_data.pop('triggers_identified', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if triggers is not None:
            instance.triggers_identified.set(triggers)
        return instance


class MigraineAttackListSerializer(serializers.ModelSerializer):
    trigger_count = serializers.IntegerField(source='triggers_identified.count', read_only=True)

    class Meta:
        model = MigraineAttack
        fields = [
            'id', 'start_datetime', 'duration_minutes',
            'intensity', 'pain_location', 'has_aura',
            'medication_taken', 'trigger_count', 'created_at',
        ]


class MigraineStatsSerializer(serializers.Serializer):
    total_attacks = serializers.IntegerField()
    avg_intensity = serializers.FloatField()
    avg_duration = serializers.FloatField()
    attacks_this_month = serializers.IntegerField()
    attacks_last_month = serializers.IntegerField()
    most_common_triggers = serializers.ListField()
    most_common_location = serializers.CharField()
    aura_percentage = serializers.FloatField()
