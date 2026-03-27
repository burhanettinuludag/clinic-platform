from rest_framework import serializers
from .models import (
    ParkinsonTrigger, ParkinsonSymptomEntry,
    ParkinsonMedication, ParkinsonMedicationSchedule, ParkinsonMedicationLog,
    HoehnYahrAssessment, SchwabEnglandAssessment, NMSQuestAssessment,
    NoseraMotorAssessment, NoseraDailyLivingAssessment,
    ParkinsonVisit,
)


# ============================================================
# TETİKLEYİCİLER
# ============================================================

class ParkinsonTriggerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ParkinsonTrigger
        fields = ['id', 'name', 'name_tr', 'name_en', 'category', 'is_predefined']

    def get_name(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'tr') if request else 'tr'
        return obj.name_tr if lang == 'tr' else (obj.name_en or obj.name_tr)


# ============================================================
# SEMPTOM GÜNLÜKLERİ
# ============================================================

class ParkinsonSymptomEntrySerializer(serializers.ModelSerializer):
    triggers_identified = ParkinsonTriggerSerializer(many=True, read_only=True)
    trigger_ids = serializers.PrimaryKeyRelatedField(
        queryset=ParkinsonTrigger.objects.all(),
        many=True, write_only=True, required=False, source='triggers_identified',
    )

    class Meta:
        model = ParkinsonSymptomEntry
        fields = [
            'id', 'recorded_at', 'motor_state', 'affected_side',
            'tremor_severity', 'rigidity_severity', 'bradykinesia_severity',
            'postural_instability', 'gait_difficulty',
            'has_freezing', 'has_balance_problem', 'has_speech_difficulty',
            'has_swallowing_difficulty', 'has_sleep_disturbance',
            'has_constipation', 'has_mood_change', 'has_cognitive_issue',
            'has_pain', 'has_fatigue',
            'overall_severity', 'on_time_hours', 'off_time_hours',
            'triggers_identified', 'trigger_ids', 'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ============================================================
# İLAÇ YÖNETİMİ
# ============================================================

class ParkinsonMedicationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkinsonMedicationSchedule
        fields = ['id', 'time_of_day', 'label', 'is_enabled']
        read_only_fields = ['id']


class ParkinsonMedicationSerializer(serializers.ModelSerializer):
    schedules = ParkinsonMedicationScheduleSerializer(many=True, read_only=True)
    daily_led = serializers.ReadOnlyField()

    class Meta:
        model = ParkinsonMedication
        fields = [
            'id', 'name', 'generic_name', 'drug_class', 'dosage_mg',
            'frequency_per_day', 'led_conversion_factor', 'daily_led',
            'start_date', 'end_date', 'is_active', 'notes',
            'schedules', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ParkinsonMedicationLogSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = ParkinsonMedicationLog
        fields = [
            'id', 'medication', 'medication_name', 'schedule',
            'scheduled_time', 'taken_at', 'was_taken',
            'motor_state_before', 'motor_state_after', 'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ============================================================
# KLİNİK DEĞERLENDİRMELER
# ============================================================

class HoehnYahrSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    class Meta:
        model = HoehnYahrAssessment
        fields = ['id', 'assessed_at', 'stage', 'stage_display', 'assessed_by', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SchwabEnglandSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchwabEnglandAssessment
        fields = ['id', 'assessed_at', 'score', 'assessed_by', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class NMSQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NMSQuestAssessment
        fields = [
            'id', 'assessed_at',
            'q1_drooling', 'q2_dysphagia', 'q3_constipation',
            'q4_urinary_urgency', 'q5_nocturia',
            'q6_dizziness', 'q7_sweating', 'q8_sexual_dysfunction',
            'q9_insomnia', 'q10_daytime_sleepiness', 'q11_rbd', 'q12_restless_legs',
            'q13_depression', 'q14_anxiety', 'q15_apathy',
            'q16_attention_difficulty', 'q17_memory_problem', 'q18_hallucination',
            'q19_pain', 'q20_numbness', 'q21_taste_smell',
            'q22_weight_change', 'q23_fatigue', 'q24_double_vision',
            'q25_speech', 'q26_falling', 'q27_freezing',
            'q28_leg_swelling', 'q29_excessive_saliva', 'q30_unexplained_fever',
            'total_score', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'total_score', 'created_at']

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance


class NoseraMotorSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoseraMotorAssessment
        fields = [
            'id', 'assessed_at',
            'tremor_rest', 'tremor_action', 'rigidity',
            'finger_tapping', 'hand_movements', 'leg_agility',
            'arising_from_chair', 'gait', 'postural_stability', 'body_bradykinesia',
            'total_score', 'assessed_by', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'total_score', 'created_at']

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance


class NoseraDailyLivingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoseraDailyLivingAssessment
        fields = [
            'id', 'assessed_at',
            'speech', 'salivation', 'swallowing', 'handwriting',
            'cutting_food', 'dressing', 'hygiene', 'turning_in_bed',
            'falling', 'freezing', 'walking', 'tremor_impact',
            'total_score', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'total_score', 'created_at']

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.calculate_total()
        instance.save(update_fields=['total_score'])
        return instance


# ============================================================
# VİZİT KAYDI
# ============================================================

class ParkinsonVisitSerializer(serializers.ModelSerializer):
    visit_type_display = serializers.CharField(source='get_visit_type_display', read_only=True)
    hoehn_yahr_detail = HoehnYahrSerializer(source='hoehn_yahr', read_only=True)
    schwab_england_detail = SchwabEnglandSerializer(source='schwab_england', read_only=True)

    class Meta:
        model = ParkinsonVisit
        fields = [
            'id', 'visit_date', 'visit_type', 'visit_type_display',
            'doctor_name', 'hospital_name',
            'hoehn_yahr', 'hoehn_yahr_detail',
            'schwab_england', 'schwab_england_detail',
            'total_daily_led', 'medication_changes', 'findings', 'plan',
            'next_visit_date', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ============================================================
# DASHBOARD / İSTATİSTİK
# ============================================================

class ParkinsonDashboardSerializer(serializers.Serializer):
    """Parkinson dashboard istatistikleri."""
    total_symptoms = serializers.IntegerField()
    total_medications = serializers.IntegerField()
    active_medications = serializers.IntegerField()
    total_daily_led = serializers.FloatField()
    latest_hoehn_yahr = HoehnYahrSerializer(allow_null=True)
    latest_schwab_england = SchwabEnglandSerializer(allow_null=True)
    avg_on_time = serializers.FloatField(allow_null=True)
    avg_off_time = serializers.FloatField(allow_null=True)
    recent_symptoms = ParkinsonSymptomEntrySerializer(many=True)
    upcoming_medications = ParkinsonMedicationLogSerializer(many=True)
    next_visit = ParkinsonVisitSerializer(allow_null=True)
