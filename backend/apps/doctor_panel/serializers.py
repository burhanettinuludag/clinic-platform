from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import CustomUser, PatientProfile
from apps.patients.models import PatientModule, TaskCompletion
from apps.tracking.models import SymptomEntry, MedicationLog
from apps.migraine.models import MigraineAttack
from .models import DoctorNote


class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    enrolled_modules = serializers.SerializerMethodField()
    last_active = serializers.DateTimeField()
    alert_flags = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone', 'date_of_birth',
            'gender', 'enrolled_modules', 'last_active', 'alert_flags',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_date_of_birth(self, obj):
        profile = getattr(obj, 'patient_profile', None)
        return profile.date_of_birth if profile else None

    def get_gender(self, obj):
        profile = getattr(obj, 'patient_profile', None)
        return profile.gender if profile else ''

    def get_enrolled_modules(self, obj):
        modules = PatientModule.objects.filter(
            patient=obj, is_active=True
        ).select_related('disease_module')
        lang = self._get_lang()
        return [
            {
                'id': str(pm.disease_module.id),
                'name': getattr(pm.disease_module, f'name_{lang}', pm.disease_module.name_tr),
                'disease_type': pm.disease_module.disease_type,
            }
            for pm in modules
        ]

    def get_alert_flags(self, obj):
        now = timezone.now()
        flags = []

        # 3+ gün giriş yok
        if obj.last_active and (now - obj.last_active) > timedelta(days=3):
            days = (now - obj.last_active).days
            flags.append({
                'type': 'inactive',
                'severity': 'warning' if days < 7 else 'critical',
                'message': f'{days} gündür giriş yapmadı',
            })

        # Son 7 günde görev tamamlama oranı < %50
        week_ago = (now - timedelta(days=7)).date()
        completions_count = TaskCompletion.objects.filter(
            patient=obj, completed_date__gte=week_ago
        ).count()
        if completions_count < 4:
            flags.append({
                'type': 'low_task_completion',
                'severity': 'warning',
                'message': f'Son 7 günde sadece {completions_count} görev tamamladı',
            })

        # Son 30 günde migren atak sayısı >= 8
        month_ago = now - timedelta(days=30)
        attack_count = MigraineAttack.objects.filter(
            patient=obj, start_datetime__gte=month_ago
        ).count()
        if attack_count >= 8:
            flags.append({
                'type': 'high_attack_frequency',
                'severity': 'critical',
                'message': f'Son 30 günde {attack_count} migren atağı',
            })

        return flags

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'


class PatientDetailSerializer(PatientListSerializer):
    emergency_contact_name = serializers.SerializerMethodField()
    emergency_contact_phone = serializers.SerializerMethodField()
    notes_text = serializers.SerializerMethodField()

    class Meta(PatientListSerializer.Meta):
        fields = PatientListSerializer.Meta.fields + [
            'emergency_contact_name', 'emergency_contact_phone',
            'notes_text', 'date_joined',
        ]

    def get_emergency_contact_name(self, obj):
        profile = getattr(obj, 'patient_profile', None)
        return profile.emergency_contact_name if profile else ''

    def get_emergency_contact_phone(self, obj):
        profile = getattr(obj, 'patient_profile', None)
        return profile.emergency_contact_phone if profile else ''

    def get_notes_text(self, obj):
        profile = getattr(obj, 'patient_profile', None)
        return profile.notes if profile else ''


class TimelineEntrySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    entry_type = serializers.CharField()
    date = serializers.DateTimeField()
    title = serializers.CharField()
    detail = serializers.CharField(allow_blank=True)
    severity = serializers.CharField(allow_blank=True, required=False)
    metadata = serializers.DictField(required=False)


class DoctorNoteSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorNote
        fields = [
            'id', 'doctor', 'patient', 'note_type', 'content',
            'is_private', 'doctor_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'doctor', 'doctor_name', 'created_at', 'updated_at']

    def get_doctor_name(self, obj):
        return obj.doctor.get_full_name()


class CreateDoctorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorNote
        fields = ['patient', 'note_type', 'content', 'is_private']

    def validate_patient(self, value):
        request = self.context['request']
        if not hasattr(value, 'patient_profile') or \
           value.patient_profile.assigned_doctor != request.user:
            raise serializers.ValidationError('Bu hasta size atanmamış.')
        return value


class AlertSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    patient_name = serializers.CharField()
    alert_type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    created_at = serializers.DateTimeField()


class DashboardStatsSerializer(serializers.Serializer):
    total_patients = serializers.IntegerField()
    active_patients_7d = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    warning_alerts = serializers.IntegerField()
    avg_task_completion_rate = serializers.FloatField()
    total_attacks_30d = serializers.IntegerField()
