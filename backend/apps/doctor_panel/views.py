from drf_spectacular.utils import extend_schema_view, extend_schema
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
from apps.dementia.models import ExerciseSession, DailyAssessment, CaregiverNote, CognitiveScore
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


class DementiaReportView(generics.GenericAPIView):
    """Demans hastası ilerleme raporu."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request, patient_id):
        # Hasta kontrolü
        try:
            patient = CustomUser.objects.get(
                id=patient_id,
                patient_profile__assigned_doctor=request.user,
                role='patient',
            )
        except CustomUser.DoesNotExist:
            return Response({'error': 'Hasta bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        days = int(request.query_params.get('days', 30))
        since = now - timedelta(days=days)

        # Egzersiz istatistikleri
        sessions = ExerciseSession.objects.filter(
            patient=patient,
            started_at__gte=since
        ).select_related('exercise')

        total_sessions = sessions.count()
        completed_sessions = sessions.filter(completed_at__isnull=False).count()
        avg_accuracy = sessions.aggregate(avg=Avg('accuracy_percent'))['avg']
        total_duration = sum(s.duration_seconds or 0 for s in sessions)

        # Egzersiz türlerine göre dağılım
        exercise_by_type = {}
        for session in sessions:
            ex_type = session.exercise.exercise_type
            if ex_type not in exercise_by_type:
                exercise_by_type[ex_type] = {
                    'type': ex_type,
                    'type_display': session.exercise.get_exercise_type_display(),
                    'count': 0,
                    'total_score': 0,
                    'avg_score': 0,
                }
            exercise_by_type[ex_type]['count'] += 1
            if session.accuracy_percent:
                exercise_by_type[ex_type]['total_score'] += float(session.accuracy_percent)

        for ex_type in exercise_by_type:
            count = exercise_by_type[ex_type]['count']
            if count > 0:
                exercise_by_type[ex_type]['avg_score'] = round(
                    exercise_by_type[ex_type]['total_score'] / count, 1
                )

        # Günlük değerlendirmeler
        assessments = DailyAssessment.objects.filter(
            patient=patient,
            assessment_date__gte=since.date()
        ).order_by('-assessment_date')

        assessment_count = assessments.count()
        avg_mood = assessments.aggregate(avg=Avg('mood_score'))['avg']
        avg_confusion = assessments.aggregate(avg=Avg('confusion_level'))['avg']
        avg_sleep_quality = assessments.aggregate(avg=Avg('sleep_quality'))['avg']

        # Olaylar
        falls = assessments.filter(fall_occurred=True).count()
        wanderings = assessments.filter(wandering_occurred=True).count()
        missed_meds = assessments.filter(medication_missed=True).count()

        # ADL (Günlük yaşam aktiviteleri) ortalamaları
        adl_stats = assessments.aggregate(
            eating=Avg('eating_independence'),
            dressing=Avg('dressing_independence'),
            hygiene=Avg('hygiene_independence'),
            mobility=Avg('mobility_independence'),
            communication=Avg('verbal_communication'),
        )

        # Bakıcı notları (doktora iletilen)
        flagged_notes = CaregiverNote.objects.filter(
            patient=patient,
            is_flagged_for_doctor=True,
            created_at__gte=since
        ).order_by('-created_at')

        unreviewed_notes = flagged_notes.filter(doctor_reviewed=False).count()

        # Bilişsel skor trendi
        cognitive_scores = CognitiveScore.objects.filter(
            patient=patient,
            score_date__gte=since.date()
        ).order_by('score_date')

        score_trend = []
        for score in cognitive_scores:
            score_trend.append({
                'date': score.score_date,
                'memory': float(score.memory_score) if score.memory_score else None,
                'attention': float(score.attention_score) if score.attention_score else None,
                'language': float(score.language_score) if score.language_score else None,
                'problem_solving': float(score.problem_solving_score) if score.problem_solving_score else None,
                'overall': float(score.overall_score) if score.overall_score else None,
            })

        # Haftalık performans trendi
        weekly_performance = []
        for i in range(min(4, days // 7)):
            week_start = now - timedelta(days=(i + 1) * 7)
            week_end = now - timedelta(days=i * 7)
            week_sessions = sessions.filter(
                started_at__gte=week_start,
                started_at__lt=week_end
            )
            week_avg = week_sessions.aggregate(avg=Avg('accuracy_percent'))['avg']
            weekly_performance.append({
                'week': i + 1,
                'start_date': week_start.date(),
                'end_date': week_end.date(),
                'sessions_count': week_sessions.count(),
                'avg_accuracy': round(float(week_avg), 1) if week_avg else None,
            })

        # Son egzersiz oturumları
        recent_sessions = []
        for session in sessions.order_by('-started_at')[:10]:
            recent_sessions.append({
                'id': str(session.id),
                'exercise_name': session.exercise.name_tr,
                'exercise_type': session.exercise.get_exercise_type_display(),
                'date': session.started_at,
                'score': session.score,
                'accuracy': float(session.accuracy_percent) if session.accuracy_percent else None,
                'duration_minutes': round(session.duration_seconds / 60, 1) if session.duration_seconds else None,
            })

        # Son değerlendirmeler
        recent_assessments = []
        for assessment in assessments[:7]:
            recent_assessments.append({
                'date': assessment.assessment_date,
                'mood_score': assessment.mood_score,
                'confusion_level': assessment.confusion_level,
                'sleep_quality': assessment.sleep_quality,
                'sleep_hours': float(assessment.sleep_hours) if assessment.sleep_hours else None,
                'fall_occurred': assessment.fall_occurred,
                'wandering_occurred': assessment.wandering_occurred,
                'medication_missed': assessment.medication_missed,
                'notes': assessment.notes,
                'concerns': assessment.concerns,
            })

        # Flagged notları formatla
        notes_list = []
        for note in flagged_notes[:10]:
            notes_list.append({
                'id': str(note.id),
                'title': note.title,
                'content': note.content,
                'note_type': note.note_type,
                'severity': note.severity,
                'created_at': note.created_at,
                'doctor_reviewed': note.doctor_reviewed,
            })

        report = {
            'patient': {
                'id': str(patient.id),
                'full_name': patient.get_full_name(),
                'email': patient.email,
                'date_of_birth': patient.date_of_birth,
            },
            'report_period': {
                'days': days,
                'start_date': since.date(),
                'end_date': now.date(),
            },
            'exercise_summary': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'avg_accuracy': round(float(avg_accuracy), 1) if avg_accuracy else None,
                'total_duration_minutes': round(total_duration / 60, 1),
                'by_type': list(exercise_by_type.values()),
            },
            'assessment_summary': {
                'total_assessments': assessment_count,
                'avg_mood_score': round(float(avg_mood), 1) if avg_mood else None,
                'avg_confusion_level': round(float(avg_confusion), 1) if avg_confusion else None,
                'avg_sleep_quality': round(float(avg_sleep_quality), 1) if avg_sleep_quality else None,
                'incidents': {
                    'falls': falls,
                    'wanderings': wanderings,
                    'missed_medications': missed_meds,
                },
                'adl_scores': {
                    'eating': round(float(adl_stats['eating']), 1) if adl_stats['eating'] else None,
                    'dressing': round(float(adl_stats['dressing']), 1) if adl_stats['dressing'] else None,
                    'hygiene': round(float(adl_stats['hygiene']), 1) if adl_stats['hygiene'] else None,
                    'mobility': round(float(adl_stats['mobility']), 1) if adl_stats['mobility'] else None,
                    'communication': round(float(adl_stats['communication']), 1) if adl_stats['communication'] else None,
                },
            },
            'caregiver_notes': {
                'total_flagged': flagged_notes.count(),
                'unreviewed': unreviewed_notes,
                'notes': notes_list,
            },
            'cognitive_score_trend': score_trend,
            'weekly_performance': weekly_performance,
            'recent_sessions': recent_sessions,
            'recent_assessments': recent_assessments,
        }

        return Response(report)
