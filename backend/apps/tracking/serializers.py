from rest_framework import serializers
from .models import SymptomDefinition, SymptomEntry, Medication, MedicationLog, ReminderConfig


class SymptomDefinitionSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = SymptomDefinition
        fields = [
            'id', 'disease_module', 'key', 'label', 'label_tr', 'label_en',
            'input_type', 'config', 'order', 'is_active',
        ]

    def get_label(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            lang = request.headers.get('Accept-Language', 'tr')[:2]
        else:
            lang = 'tr'
        return getattr(obj, f'label_{lang}', obj.label_tr)


class SymptomEntrySerializer(serializers.ModelSerializer):
    symptom_key = serializers.CharField(source='symptom_definition.key', read_only=True)
    symptom_label = serializers.SerializerMethodField()

    class Meta:
        model = SymptomEntry
        fields = [
            'id', 'symptom_definition', 'symptom_key', 'symptom_label',
            'recorded_date', 'value', 'notes',
        ]

    def get_symptom_label(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            lang = request.headers.get('Accept-Language', 'tr')[:2]
        else:
            lang = 'tr'
        return getattr(obj.symptom_definition, f'label_{lang}', obj.symptom_definition.label_tr)


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'dosage', 'frequency', 'start_date',
            'end_date', 'is_active', 'notes',
        ]


class MedicationLogSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = MedicationLog
        fields = ['id', 'medication', 'medication_name', 'taken_at', 'was_taken', 'notes']


class ReminderConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderConfig
        fields = [
            'id', 'reminder_type', 'title', 'time_of_day',
            'days_of_week', 'is_enabled', 'linked_medication',
        ]
