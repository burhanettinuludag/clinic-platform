from rest_framework import serializers
from .models import SeizureEvent, EpilepsyTrigger


class EpilepsyTriggerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = EpilepsyTrigger
        fields = ['id', 'name', 'name_tr', 'name_en', 'category', 'is_predefined', 'created_by']
        read_only_fields = ['created_by']

    def get_name(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            lang = request.headers.get('Accept-Language', 'tr')[:2]
        else:
            lang = 'tr'
        return getattr(obj, f'name_{lang}', obj.name_tr)


class SeizureEventSerializer(serializers.ModelSerializer):
    triggers_identified = EpilepsyTriggerSerializer(many=True, read_only=True)
    trigger_ids = serializers.PrimaryKeyRelatedField(
        queryset=EpilepsyTrigger.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='triggers_identified',
    )

    class Meta:
        model = SeizureEvent
        fields = [
            'id', 'seizure_datetime', 'seizure_type', 'duration_seconds',
            'intensity', 'triggers_identified', 'trigger_ids',
            'loss_of_consciousness', 'medication_taken',
            'post_ictal_notes', 'notes', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_intensity(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Intensity must be between 1 and 10.")
        return value

    def create(self, validated_data):
        triggers = validated_data.pop('triggers_identified', [])
        event = SeizureEvent.objects.create(**validated_data)
        if triggers:
            event.triggers_identified.set(triggers)
        return event

    def update(self, instance, validated_data):
        triggers = validated_data.pop('triggers_identified', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if triggers is not None:
            instance.triggers_identified.set(triggers)
        return instance


class SeizureEventListSerializer(serializers.ModelSerializer):
    trigger_count = serializers.IntegerField(source='triggers_identified.count', read_only=True)

    class Meta:
        model = SeizureEvent
        fields = [
            'id', 'seizure_datetime', 'seizure_type', 'duration_seconds',
            'intensity', 'loss_of_consciousness', 'medication_taken',
            'trigger_count', 'created_at',
        ]


class SeizureStatsSerializer(serializers.Serializer):
    total_seizures = serializers.IntegerField()
    avg_intensity = serializers.FloatField()
    avg_duration = serializers.FloatField()
    seizures_this_month = serializers.IntegerField()
    seizures_last_month = serializers.IntegerField()
    most_common_triggers = serializers.ListField()
    most_common_type = serializers.CharField()
    consciousness_loss_percentage = serializers.FloatField()
