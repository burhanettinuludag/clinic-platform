from datetime import timedelta
from django.db.models import Avg, Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsPatient
from .models import (
    ParkinsonTrigger, ParkinsonSymptomEntry,
    ParkinsonMedication, ParkinsonMedicationSchedule, ParkinsonMedicationLog,
    HoehnYahrAssessment, SchwabEnglandAssessment, NMSQuestAssessment,
    NoseraMotorAssessment, NoseraDailyLivingAssessment,
    ParkinsonVisit,
)
from .serializers import (
    ParkinsonTriggerSerializer, ParkinsonSymptomEntrySerializer,
    ParkinsonMedicationSerializer, ParkinsonMedicationScheduleSerializer,
    ParkinsonMedicationLogSerializer,
    HoehnYahrSerializer, SchwabEnglandSerializer, NMSQuestSerializer,
    NoseraMotorSerializer, NoseraDailyLivingSerializer,
    ParkinsonVisitSerializer, ParkinsonDashboardSerializer,
)


class ParkinsonTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    """Parkinson tetikleyicileri (ön tanımlı + hastanın özel)."""
    serializer_class = ParkinsonTriggerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ParkinsonTrigger.objects.filter(
            is_predefined=True
        ) | ParkinsonTrigger.objects.filter(
            created_by=self.request.user
        )


class ParkinsonSymptomViewSet(viewsets.ModelViewSet):
    """Parkinson semptom günlüğü CRUD."""
    serializer_class = ParkinsonSymptomEntrySerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return ParkinsonSymptomEntry.objects.filter(
            patient=self.request.user
        ).prefetch_related('triggers_identified')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Son 30 günlük semptom trend verisi."""
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        entries = self.get_queryset().filter(recorded_at__gte=since).order_by('recorded_at')
        data = []
        for e in entries:
            data.append({
                'date': e.recorded_at.date().isoformat(),
                'motor_state': e.motor_state,
                'tremor': e.tremor_severity,
                'rigidity': e.rigidity_severity,
                'bradykinesia': e.bradykinesia_severity,
                'overall': e.overall_severity,
                'on_time': float(e.on_time_hours) if e.on_time_hours else None,
                'off_time': float(e.off_time_hours) if e.off_time_hours else None,
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Özet istatistikler."""
        qs = self.get_queryset()
        last_30 = qs.filter(recorded_at__gte=timezone.now() - timedelta(days=30))

        return Response({
            'total_entries': qs.count(),
            'last_30_days': last_30.count(),
            'avg_overall_severity': last_30.aggregate(avg=Avg('overall_severity'))['avg'],
            'avg_tremor': last_30.aggregate(avg=Avg('tremor_severity'))['avg'],
            'avg_rigidity': last_30.aggregate(avg=Avg('rigidity_severity'))['avg'],
            'avg_bradykinesia': last_30.aggregate(avg=Avg('bradykinesia_severity'))['avg'],
            'avg_on_time': last_30.aggregate(avg=Avg('on_time_hours'))['avg'],
            'avg_off_time': last_30.aggregate(avg=Avg('off_time_hours'))['avg'],
        })


class ParkinsonMedicationViewSet(viewsets.ModelViewSet):
    """Parkinson ilaçları CRUD + LED hesaplama."""
    serializer_class = ParkinsonMedicationSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return ParkinsonMedication.objects.filter(
            patient=self.request.user
        ).prefetch_related('schedules')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def led_summary(self, request):
        """Toplam günlük LED hesapla."""
        active_meds = self.get_queryset().filter(is_active=True)
        total_led = sum(med.daily_led for med in active_meds)
        meds_detail = [
            {
                'name': med.name,
                'drug_class': med.drug_class,
                'dosage_mg': float(med.dosage_mg),
                'frequency': med.frequency_per_day,
                'led_factor': float(med.led_conversion_factor),
                'daily_led': med.daily_led,
            }
            for med in active_meds
        ]
        return Response({
            'total_daily_led': total_led,
            'medications': meds_detail,
        })


class MedicationScheduleViewSet(viewsets.ModelViewSet):
    """İlaç alım saatleri yönetimi."""
    serializer_class = ParkinsonMedicationScheduleSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        med_id = self.kwargs.get('medication_pk')
        return ParkinsonMedicationSchedule.objects.filter(
            medication_id=med_id,
            medication__patient=self.request.user,
        )

    def perform_create(self, serializer):
        med_id = self.kwargs.get('medication_pk')
        medication = ParkinsonMedication.objects.get(
            id=med_id, patient=self.request.user,
        )
        serializer.save(medication=medication)


class ParkinsonMedicationLogViewSet(viewsets.ModelViewSet):
    """İlaç alım kayıtları."""
    serializer_class = ParkinsonMedicationLogSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return ParkinsonMedicationLog.objects.filter(
            medication__patient=self.request.user,
        ).select_related('medication')

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugünkü ilaç programı ve alım durumu."""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        logs = self.get_queryset().filter(
            scheduled_time__gte=today_start,
            scheduled_time__lt=today_end,
        ).order_by('scheduled_time')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def take(self, request, pk=None):
        """İlacı alındı olarak işaretle."""
        log = self.get_object()
        log.was_taken = True
        log.taken_at = timezone.now()
        log.motor_state_before = request.data.get('motor_state_before', '')
        log.save(update_fields=['was_taken', 'taken_at', 'motor_state_before', 'updated_at'])
        return Response(self.get_serializer(log).data)


class HoehnYahrViewSet(viewsets.ModelViewSet):
    serializer_class = HoehnYahrSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return HoehnYahrAssessment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class SchwabEnglandViewSet(viewsets.ModelViewSet):
    serializer_class = SchwabEnglandSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return SchwabEnglandAssessment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class NMSQuestViewSet(viewsets.ModelViewSet):
    serializer_class = NMSQuestSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return NMSQuestAssessment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class NoseraMotorViewSet(viewsets.ModelViewSet):
    serializer_class = NoseraMotorSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return NoseraMotorAssessment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class NoseraDailyLivingViewSet(viewsets.ModelViewSet):
    serializer_class = NoseraDailyLivingSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return NoseraDailyLivingAssessment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class ParkinsonVisitViewSet(viewsets.ModelViewSet):
    serializer_class = ParkinsonVisitSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return ParkinsonVisit.objects.filter(
            patient=self.request.user
        ).select_related('hoehn_yahr', 'schwab_england')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class ParkinsonDashboardView(viewsets.ViewSet):
    """Parkinson dashboard - özet veriler."""
    permission_classes = [IsPatient]

    def list(self, request):
        user = request.user
        now = timezone.now()

        # İlaçlar
        active_meds = ParkinsonMedication.objects.filter(patient=user, is_active=True)
        total_led = sum(med.daily_led for med in active_meds)

        # Son değerlendirmeler
        latest_hy = HoehnYahrAssessment.objects.filter(patient=user).first()
        latest_se = SchwabEnglandAssessment.objects.filter(patient=user).first()

        # Son 7 gün semptom
        recent_symptoms = ParkinsonSymptomEntry.objects.filter(
            patient=user,
            recorded_at__gte=now - timedelta(days=7),
        ).prefetch_related('triggers_identified')[:10]

        # ON/OFF ortalama (son 30 gün)
        last_30 = ParkinsonSymptomEntry.objects.filter(
            patient=user,
            recorded_at__gte=now - timedelta(days=30),
        )
        avg_times = last_30.aggregate(
            avg_on=Avg('on_time_hours'),
            avg_off=Avg('off_time_hours'),
        )

        # Bugünkü ilaç logları
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        upcoming_logs = ParkinsonMedicationLog.objects.filter(
            medication__patient=user,
            scheduled_time__gte=today_start,
            scheduled_time__lt=today_start + timedelta(days=1),
        ).select_related('medication').order_by('scheduled_time')[:20]

        # Sonraki vizit
        next_visit = ParkinsonVisit.objects.filter(
            patient=user,
            visit_date__gte=now,
        ).order_by('visit_date').first()

        data = {
            'total_symptoms': ParkinsonSymptomEntry.objects.filter(patient=user).count(),
            'total_medications': ParkinsonMedication.objects.filter(patient=user).count(),
            'active_medications': active_meds.count(),
            'total_daily_led': total_led,
            'latest_hoehn_yahr': HoehnYahrSerializer(latest_hy).data if latest_hy else None,
            'latest_schwab_england': SchwabEnglandSerializer(latest_se).data if latest_se else None,
            'avg_on_time': avg_times['avg_on'],
            'avg_off_time': avg_times['avg_off'],
            'recent_symptoms': ParkinsonSymptomEntrySerializer(recent_symptoms, many=True).data,
            'upcoming_medications': ParkinsonMedicationLogSerializer(upcoming_logs, many=True).data,
            'next_visit': ParkinsonVisitSerializer(next_visit).data if next_visit else None,
        }
        return Response(data)
