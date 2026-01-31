from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta

from apps.accounts.models import CustomUser, PatientProfile
from apps.accounts.permissions import IsDoctor
from apps.patients.models import TaskCompletion, TaskTemplate
from apps.tracking.models import SymptomEntry, MedicationLog
from apps.migraine.models import MigraineAttack
from .models import DoctorNote
from .serializers import (
    PatientListSerializer,
    PatientDetailSerializer,
    TimelineEntrySerializer,
    DoctorNoteSerializer,
    CreateDoctorNoteSerializer,
    AlertSerializer,
    DashboardStatsSerializer,
)


class DoctorPatientViewSet(viewsets.ReadOnlyModelViewSet):
    """Hekim paneli - Hasta listesi ve detayı."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientListSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(
            patient_profile__assigned_doctor=self.request.user,
            role='patient',
        ).select_related('patient_profile').order_by('first_name', 'last_name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtreler
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        module_filter = request.query_params.get('module')
        if module_filter:
            queryset = queryset.filter(
                enrolled_modules__disease_module__disease_type=module_filter,
                enrolled_modules__is_active=True,
            )

        alert_filter = request.query_params.get('has_alerts')
        if alert_filter == 'true':
            three_days_ago = timezone.now() - timedelta(days=3)
            queryset = queryset.filter(
                Q(last_active__lt=three_days_ago) | Q(last_active__isnull=True)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Hasta timeline: atak, semptom, görev tamamlama, ilaç logları."""
        patient = self.get_object()
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        entries = []

        # Migren atakları
        attacks = MigraineAttack.objects.filter(
            patient=patient, start_datetime__gte=since
        ).order_by('-start_datetime')
        for attack in attacks:
            entries.append({
                'id': attack.id,
                'entry_type': 'migraine_attack',
                'date': attack.start_datetime,
                'title': f'Migren Atağı (Şiddet: {attack.intensity}/10)',
                'detail': f'Süre: {attack.duration_minutes or "?"} dk, Lokasyon: {attack.pain_location}',
                'severity': 'critical' if attack.intensity >= 7 else 'warning' if attack.intensity >= 4 else 'info',
                'metadata': {
                    'intensity': attack.intensity,
                    'duration_minutes': attack.duration_minutes,
                    'has_aura': attack.has_aura,
                    'medication_taken': attack.medication_taken,
                },
            })

        # Görev tamamlamaları
        completions = TaskCompletion.objects.filter(
            patient=patient, created_at__gte=since
        ).select_related('task_template').order_by('-created_at')
        for tc in completions:
            entries.append({
                'id': tc.id,
                'entry_type': 'task_completion',
                'date': tc.created_at,
                'title': f'Görev: {tc.task_template.title_tr}',
                'detail': tc.notes,
                'metadata': {
                    'task_type': tc.task_template.task_type,
                    'response_data': tc.response_data,
                },
            })

        # Semptom kayıtları
        symptoms = SymptomEntry.objects.filter(
            patient=patient, created_at__gte=since
        ).select_related('symptom_definition').order_by('-created_at')
        for se in symptoms:
            entries.append({
                'id': se.id,
                'entry_type': 'symptom_entry',
                'date': se.created_at,
                'title': f'Semptom: {se.symptom_definition.label_tr}',
                'detail': f'Değer: {se.value}',
                'metadata': {
                    'symptom_key': se.symptom_definition.key,
                    'value': se.value,
                },
            })

        # İlaç logları
        med_logs = MedicationLog.objects.filter(
            patient=patient, taken_at__gte=since
        ).select_related('medication').order_by('-taken_at')
        for ml in med_logs:
            status_text = 'Alındı' if ml.was_taken else 'Atlandı'
            entries.append({
                'id': ml.id,
                'entry_type': 'medication_log',
                'date': ml.taken_at,
                'title': f'İlaç: {ml.medication.name}',
                'detail': f'{ml.medication.dosage} - {status_text}',
                'severity': 'info' if ml.was_taken else 'warning',
                'metadata': {
                    'medication_name': ml.medication.name,
                    'was_taken': ml.was_taken,
                },
            })

        # Doktor notları
        notes = DoctorNote.objects.filter(
            patient=patient, doctor=request.user, created_at__gte=since
        ).order_by('-created_at')
        for note in notes:
            entries.append({
                'id': note.id,
                'entry_type': 'doctor_note',
                'date': note.created_at,
                'title': f'Not ({note.get_note_type_display()})',
                'detail': note.content[:200],
                'metadata': {
                    'note_type': note.note_type,
                    'is_private': note.is_private,
                },
            })

        # Tarihe göre sırala
        entries.sort(key=lambda x: x['date'], reverse=True)
        serializer = TimelineEntrySerializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        """Hasta notları listele veya yeni not ekle."""
        patient = self.get_object()

        if request.method == 'GET':
            notes = DoctorNote.objects.filter(
                patient=patient, doctor=request.user
            )
            serializer = DoctorNoteSerializer(notes, many=True)
            return Response(serializer.data)

        # POST
        serializer = CreateDoctorNoteSerializer(
            data={**request.data, 'patient': patient.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=request.user)
        return Response(
            DoctorNoteSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )


class AlertListView(generics.ListAPIView):
    """Tüm uyarı bayrakları."""
    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = AlertSerializer

    def list(self, request, *args, **kwargs):
        patients = CustomUser.objects.filter(
            patient_profile__assigned_doctor=request.user,
            role='patient',
        ).select_related('patient_profile')

        now = timezone.now()
        alerts = []

        for patient in patients:
            # İnaktivite
            if patient.last_active and (now - patient.last_active) > timedelta(days=3):
                days = (now - patient.last_active).days
                alerts.append({
                    'patient_id': patient.id,
                    'patient_name': patient.get_full_name(),
                    'alert_type': 'inactive',
                    'severity': 'critical' if days >= 7 else 'warning',
                    'message': f'{days} gündür giriş yapmadı',
                    'created_at': patient.last_active,
                })

            # Yüksek atak sıklığı
            month_ago = now - timedelta(days=30)
            attack_count = MigraineAttack.objects.filter(
                patient=patient, start_datetime__gte=month_ago
            ).count()
            if attack_count >= 8:
                alerts.append({
                    'patient_id': patient.id,
                    'patient_name': patient.get_full_name(),
                    'alert_type': 'high_attack_frequency',
                    'severity': 'critical',
                    'message': f'Son 30 günde {attack_count} migren atağı',
                    'created_at': now,
                })

            # Düşük görev tamamlama
            week_ago = (now - timedelta(days=7)).date()
            completions = TaskCompletion.objects.filter(
                patient=patient, completed_date__gte=week_ago
            ).count()
            if completions < 3:
                alerts.append({
                    'patient_id': patient.id,
                    'patient_name': patient.get_full_name(),
                    'alert_type': 'low_task_completion',
                    'severity': 'warning',
                    'message': f'Son 7 günde sadece {completions} görev tamamladı',
                    'created_at': now,
                })

        # Severity'e göre sırala: critical önce
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 9))

        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class DashboardStatsView(generics.GenericAPIView):
    """Hekim dashboard istatistikleri."""
    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = DashboardStatsSerializer

    def get(self, request):
        patients = CustomUser.objects.filter(
            patient_profile__assigned_doctor=request.user,
            role='patient',
        )
        now = timezone.now()
        total = patients.count()

        # Son 7 günde aktif
        week_ago = now - timedelta(days=7)
        active_7d = patients.filter(last_active__gte=week_ago).count()

        # Uyarı sayıları
        three_days_ago = now - timedelta(days=3)
        critical = 0
        warning = 0
        month_ago = now - timedelta(days=30)

        for p in patients:
            if p.last_active and (now - p.last_active) > timedelta(days=7):
                critical += 1
            elif p.last_active and (now - p.last_active) > timedelta(days=3):
                warning += 1

            attacks = MigraineAttack.objects.filter(
                patient=p, start_datetime__gte=month_ago
            ).count()
            if attacks >= 8:
                critical += 1

        # Ortalama görev tamamlama oranı
        week_ago_date = (now - timedelta(days=7)).date()
        total_completions = TaskCompletion.objects.filter(
            patient__in=patients, completed_date__gte=week_ago_date
        ).count()
        expected = total * 7  # 1 görev/gün varsayımı
        avg_rate = (total_completions / expected * 100) if expected > 0 else 0

        # Toplam atak (30 gün)
        total_attacks = MigraineAttack.objects.filter(
            patient__in=patients, start_datetime__gte=month_ago
        ).count()

        data = {
            'total_patients': total,
            'active_patients_7d': active_7d,
            'critical_alerts': critical,
            'warning_alerts': warning,
            'avg_task_completion_rate': round(avg_rate, 1),
            'total_attacks_30d': total_attacks,
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
