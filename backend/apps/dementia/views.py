from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Avg, Count, Sum, Q
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient, IsCaregiver, IsRelative, IsPatientOrCaregiver
from .models import (
    CognitiveExercise,
    ExerciseSession,
    DailyAssessment,
    CaregiverNote,
    CognitiveScore,
    CognitiveScreening,
    ReportRecipient,
    ReportShareRecord,
)
from .serializers import (
    CognitiveExerciseSerializer,
    ExerciseSessionSerializer,
    ExerciseSessionCreateSerializer,
    DailyAssessmentSerializer,
    CaregiverNoteSerializer,
    CognitiveScoreSerializer,
    CognitiveStatsSerializer,
    CognitiveScreeningSerializer,
    CognitiveScreeningCreateSerializer,
    CaregiverPatientSummarySerializer,
    CaregiverAlertSerializer,
    ReportRecipientSerializer,
    ReportRecipientCreateSerializer,
    ReportShareRecordSerializer,
    ShareReportSerializer,
)


class CognitiveExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Available cognitive exercises.
    """
    serializer_class = CognitiveExerciseSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['exercise_type', 'difficulty']

    def get_queryset(self):
        return CognitiveExercise.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get exercises grouped by type."""
        exercises = self.get_queryset()
        grouped = {}
        for ex in exercises:
            ex_type = ex.exercise_type
            if ex_type not in grouped:
                grouped[ex_type] = {
                    'type': ex_type,
                    'type_display': ex.get_exercise_type_display(),
                    'exercises': [],
                }
            grouped[ex_type]['exercises'].append(
                CognitiveExerciseSerializer(ex, context={'request': request}).data
            )
        return Response(list(grouped.values()))


class ExerciseSessionViewSet(viewsets.ModelViewSet):
    """
    Patient's exercise sessions.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['exercise', 'exercise__exercise_type']

    def get_serializer_class(self):
        if self.action == 'create':
            return ExerciseSessionCreateSerializer
        return ExerciseSessionSerializer

    def get_queryset(self):
        return ExerciseSession.objects.filter(
            patient=self.request.user
        ).select_related('exercise')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent sessions (last 7 days)."""
        week_ago = timezone.now() - timedelta(days=7)
        sessions = self.get_queryset().filter(started_at__gte=week_ago)[:20]
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get exercise statistics for dashboard."""
        user = request.user
        today = date.today()
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)

        # Total exercises
        total = ExerciseSession.objects.filter(patient=user).count()

        # This week
        this_week = ExerciseSession.objects.filter(
            patient=user,
            started_at__date__gte=week_ago
        )
        this_week_count = this_week.count()
        this_week_avg = this_week.aggregate(avg=Avg('accuracy_percent'))['avg']

        # Last week
        last_week = ExerciseSession.objects.filter(
            patient=user,
            started_at__date__gte=two_weeks_ago,
            started_at__date__lt=week_ago
        )
        last_week_avg = last_week.aggregate(avg=Avg('accuracy_percent'))['avg']

        # Calculate trend
        if this_week_avg and last_week_avg:
            if this_week_avg > last_week_avg + 5:
                trend = 'improving'
            elif this_week_avg < last_week_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        # Streak calculation
        streak = 0
        check_date = today
        while True:
            has_session = ExerciseSession.objects.filter(
                patient=user,
                started_at__date=check_date
            ).exists()
            if has_session:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        # Favorite exercise type
        favorite = ExerciseSession.objects.filter(
            patient=user
        ).values('exercise__exercise_type').annotate(
            count=Count('id')
        ).order_by('-count').first()
        favorite_type = favorite['exercise__exercise_type'] if favorite else None

        # Last assessment
        last_assessment = DailyAssessment.objects.filter(
            patient=user
        ).order_by('-assessment_date').first()

        data = {
            'total_exercises_completed': total,
            'exercises_this_week': this_week_count,
            'current_streak_days': streak,
            'avg_score_this_week': round(this_week_avg, 2) if this_week_avg else None,
            'avg_score_last_week': round(last_week_avg, 2) if last_week_avg else None,
            'score_trend': trend,
            'favorite_exercise_type': favorite_type,
            'last_assessment_date': last_assessment.assessment_date if last_assessment else None,
        }

        serializer = CognitiveStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Get daily scores for charting (last 30 days)."""
        days = int(request.query_params.get('days', 30))
        start_date = date.today() - timedelta(days=days)

        sessions = self.get_queryset().filter(
            started_at__date__gte=start_date
        ).values('started_at__date').annotate(
            avg_score=Avg('accuracy_percent'),
            sessions_count=Count('id'),
            total_duration=Sum('duration_seconds'),
        ).order_by('started_at__date')

        return Response(list(sessions))

    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate PDF report for the patient's cognitive data."""
        from .reports import DementiaReportGenerator

        start_str = request.query_params.get('start_date')
        end_str = request.query_params.get('end_date')

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Gecersiz tarih formati. YYYY-MM-DD kullanin.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        generator = DementiaReportGenerator(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
        )
        buffer = generator.generate()

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"bilissel_rapor_{request.user.last_name}_{date.today().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class DailyAssessmentViewSet(viewsets.ModelViewSet):
    """
    Daily cognitive and functional assessments.
    """
    serializer_class = DailyAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOrCaregiver]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assessment_date']

    def get_queryset(self):
        return DailyAssessment.objects.filter(
            patient=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            patient=self.request.user,
            recorded_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's assessment if exists."""
        assessment = self.get_queryset().filter(
            assessment_date=date.today()
        ).first()
        if assessment:
            serializer = self.get_serializer(assessment)
            return Response(serializer.data)
        return Response(None)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Get assessment trends for charting."""
        days = int(request.query_params.get('days', 30))
        start_date = date.today() - timedelta(days=days)

        assessments = self.get_queryset().filter(
            assessment_date__gte=start_date
        ).values(
            'assessment_date',
            'mood_score', 'confusion_level', 'agitation_level',
            'sleep_quality', 'sleep_hours',
        ).order_by('assessment_date')

        return Response(list(assessments))


class CaregiverNoteViewSet(viewsets.ModelViewSet):
    """
    Notes from caregivers about the patient.
    Accessible by patients (own data) and caregivers (assigned patients).
    """
    serializer_class = CaregiverNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOrCaregiver]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['note_type', 'severity', 'is_flagged_for_doctor']

    def get_queryset(self):
        return CaregiverNote.objects.filter(
            patient=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            patient=self.request.user,
            caregiver=self.request.user
        )

    @action(detail=False, methods=['get'])
    def flagged(self, request):
        """Get notes flagged for doctor review."""
        notes = self.get_queryset().filter(
            is_flagged_for_doctor=True,
            doctor_reviewed=False
        )
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)


class CognitiveScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Aggregated cognitive scores over time.
    """
    serializer_class = CognitiveScoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_queryset(self):
        return CognitiveScore.objects.filter(
            patient=self.request.user
        )

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest cognitive score."""
        score = self.get_queryset().first()
        if score:
            serializer = self.get_serializer(score)
            return Response(serializer.data)
        return Response(None)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Get cognitive scores for charting."""
        months = int(request.query_params.get('months', 6))
        start_date = date.today() - timedelta(days=months * 30)

        scores = self.get_queryset().filter(
            score_date__gte=start_date
        ).values(
            'score_date',
            'memory_score', 'attention_score', 'language_score',
            'problem_solving_score', 'orientation_score', 'overall_score',
        ).order_by('score_date')

        return Response(list(scores))


class CognitiveScreeningViewSet(viewsets.ModelViewSet):
    """
    Cognitive Screening assessments - custom copyright-free assessment.
    Evaluates: orientation, memory, attention, language, and executive function.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_serializer_class(self):
        if self.action == 'create':
            return CognitiveScreeningCreateSerializer
        return CognitiveScreeningSerializer

    def get_queryset(self):
        return CognitiveScreening.objects.filter(
            patient=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            patient=self.request.user,
            administered_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest cognitive screening assessment."""
        assessment = self.get_queryset().first()
        if assessment:
            serializer = CognitiveScreeningSerializer(assessment)
            return Response(serializer.data)
        return Response(None)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get cognitive screening score history for charting."""
        assessments = self.get_queryset().values(
            'assessment_date', 'total_score',
            'orientation_score', 'memory_score', 'attention_score',
            'language_score', 'executive_score'
        ).order_by('assessment_date')
        return Response(list(assessments))


class CaregiverDashboardViewSet(viewsets.ViewSet):
    """
    Dashboard endpoints for caregivers to monitor their assigned patients.
    """
    permission_classes = [permissions.IsAuthenticated, IsCaregiver]

    def _get_assigned_patients(self, user):
        """Get patients assigned to this caregiver."""
        from apps.accounts.models import CaregiverProfile
        try:
            profile = CaregiverProfile.objects.get(user=user)
            return profile.patients.all()
        except CaregiverProfile.DoesNotExist:
            return user.__class__.objects.none()

    def _build_patient_summary(self, patient):
        """Build summary data for a single patient."""
        today = date.today()
        week_ago = today - timedelta(days=7)

        # Latest cognitive score
        latest_score_obj = CognitiveScore.objects.filter(
            patient=patient
        ).first()
        latest_score = latest_score_obj.overall_score if latest_score_obj else None

        # Exercises today
        exercises_today = ExerciseSession.objects.filter(
            patient=patient,
            started_at__date=today,
        ).count()

        # Exercises this week
        exercises_this_week = ExerciseSession.objects.filter(
            patient=patient,
            started_at__date__gte=week_ago,
        ).count()

        # Streak
        streak = 0
        check_date = today
        while True:
            has = ExerciseSession.objects.filter(
                patient=patient,
                started_at__date=check_date,
            ).exists()
            if has:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        # Alerts check
        has_alerts = CaregiverNote.objects.filter(
            patient=patient,
            is_flagged_for_doctor=True,
            doctor_reviewed=False,
        ).exists()
        if not has_alerts:
            has_alerts = DailyAssessment.objects.filter(
                patient=patient,
                assessment_date__gte=week_ago,
            ).filter(
                models.Q(fall_occurred=True) |
                models.Q(wandering_occurred=True) |
                models.Q(medication_missed=True)
            ).exists()

        # Last activity
        last_session = ExerciseSession.objects.filter(
            patient=patient
        ).first()
        last_activity = last_session.started_at if last_session else None

        return {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'email': patient.email,
            'latest_score': latest_score,
            'exercises_today': exercises_today,
            'exercises_this_week': exercises_this_week,
            'streak_days': streak,
            'has_alerts': has_alerts,
            'last_activity': last_activity,
        }

    @action(detail=False, methods=['get'], url_path='patients')
    def patients_list(self, request):
        """List assigned patients with summary stats."""
        patients = self._get_assigned_patients(request.user)
        summaries = [self._build_patient_summary(p) for p in patients]
        serializer = CaregiverPatientSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='patients/(?P<patient_id>[^/.]+)/summary')
    def patient_summary(self, request, patient_id=None):
        """Get detailed summary for a specific assigned patient."""
        patients = self._get_assigned_patients(request.user)
        patient = patients.filter(id=patient_id).first()
        if not patient:
            return Response(
                {'detail': 'Bu hastaya erisim izniniz yok.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        week_ago = date.today() - timedelta(days=7)
        month_ago = date.today() - timedelta(days=30)

        summary = self._build_patient_summary(patient)

        recent_sessions = ExerciseSession.objects.filter(
            patient=patient,
            started_at__date__gte=week_ago,
        ).select_related('exercise')[:20]

        recent_assessments = DailyAssessment.objects.filter(
            patient=patient,
            assessment_date__gte=week_ago,
        )[:7]

        recent_notes = CaregiverNote.objects.filter(
            patient=patient,
        ).order_by('-created_at')[:10]

        cognitive_scores = CognitiveScore.objects.filter(
            patient=patient,
            score_date__gte=month_ago,
        )[:30]

        latest_screening = CognitiveScreening.objects.filter(
            patient=patient,
        ).first()

        data = {
            'patient': summary,
            'recent_sessions': ExerciseSessionSerializer(
                recent_sessions, many=True, context={'request': request}
            ).data,
            'recent_assessments': DailyAssessmentSerializer(
                recent_assessments, many=True
            ).data,
            'recent_notes': CaregiverNoteSerializer(
                recent_notes, many=True
            ).data,
            'cognitive_scores': CognitiveScoreSerializer(
                cognitive_scores, many=True
            ).data,
            'latest_screening': CognitiveScreeningSerializer(
                latest_screening
            ).data if latest_screening else None,
        }

        return Response(data)

    @action(detail=False, methods=['get'], url_path='alerts')
    def alerts(self, request):
        """Get all alerts across assigned patients."""
        patients = self._get_assigned_patients(request.user)
        alerts = []
        week_ago = date.today() - timedelta(days=7)

        for patient in patients:
            patient_name = patient.get_full_name()

            # Flagged notes
            flagged_notes = CaregiverNote.objects.filter(
                patient=patient,
                is_flagged_for_doctor=True,
                doctor_reviewed=False,
            )
            for note in flagged_notes:
                alerts.append({
                    'alert_type': 'flagged_note',
                    'severity': note.severity,
                    'patient_id': patient.id,
                    'patient_name': patient_name,
                    'message': f'{note.get_note_type_display()}: {note.title}',
                    'timestamp': note.created_at,
                    'related_id': str(note.id),
                })

            # Incident alerts from daily assessments
            recent_assessments = DailyAssessment.objects.filter(
                patient=patient,
                assessment_date__gte=week_ago,
            )
            for assessment in recent_assessments:
                if assessment.fall_occurred:
                    alerts.append({
                        'alert_type': 'fall',
                        'severity': 3,
                        'patient_id': patient.id,
                        'patient_name': patient_name,
                        'message': f'Dusme olayi kaydedildi ({assessment.assessment_date})',
                        'timestamp': assessment.created_at,
                        'related_id': str(assessment.id),
                    })
                if assessment.wandering_occurred:
                    alerts.append({
                        'alert_type': 'wandering',
                        'severity': 3,
                        'patient_id': patient.id,
                        'patient_name': patient_name,
                        'message': f'Kaybolma/gezinme olayi ({assessment.assessment_date})',
                        'timestamp': assessment.created_at,
                        'related_id': str(assessment.id),
                    })
                if assessment.medication_missed:
                    alerts.append({
                        'alert_type': 'medication',
                        'severity': 2,
                        'patient_id': patient.id,
                        'patient_name': patient_name,
                        'message': f'Ilac atlama ({assessment.assessment_date})',
                        'timestamp': assessment.created_at,
                        'related_id': str(assessment.id),
                    })

        # Sort by severity (desc) then timestamp (desc)
        alerts.sort(key=lambda a: (-a['severity'], a['timestamp']), reverse=False)
        alerts.sort(key=lambda a: -a['severity'])

        serializer = CaregiverAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class ReportRecipientViewSet(viewsets.ModelViewSet):
    """
    Manage report recipients for sharing cognitive health reports.
    Patients can add/edit/deactivate recipients with KVKK consent.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReportRecipientCreateSerializer
        return ReportRecipientSerializer

    def get_queryset(self):
        return ReportRecipient.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            patient=self.request.user,
            consent_given_at=timezone.now(),
            consent_text=(
                'Saglik verilerimi bu kisiyle paylasmayi, KVKK kapsaminda '
                'acik rizamla onayliyorum.'
            ),
        )

    def perform_destroy(self, instance):
        # Soft delete: deactivate instead of hard delete
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=False, methods=['post'], url_path='share')
    def share_report(self, request):
        """Share a cognitive health report with a recipient."""
        from .sharing import share_report_via_email, share_report_via_telegram

        serializer = ShareReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient_id = serializer.validated_data['recipient_id']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        # Verify recipient belongs to this patient and is active
        try:
            recipient = ReportRecipient.objects.get(
                id=recipient_id,
                patient=request.user,
                is_active=True,
            )
        except ReportRecipient.DoesNotExist:
            return Response(
                {'detail': 'Alici bulunamadi veya aktif degil.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check KVKK consent
        if not recipient.consent_given_at:
            return Response(
                {'detail': 'Bu alici icin KVKK onayi verilmemis.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get client IP for audit
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        if not ip_address:
            ip_address = request.META.get('REMOTE_ADDR')

        results = []

        # Share via email
        if recipient.notify_via in ('email', 'both') and recipient.email:
            result = share_report_via_email(
                patient=request.user,
                recipient=recipient,
                start_date=start_date,
                end_date=end_date,
                ip_address=ip_address,
            )
            results.append({'channel': 'email', **result})

        # Share via telegram
        if recipient.notify_via in ('telegram', 'both') and recipient.telegram_chat_id:
            result = share_report_via_telegram(
                patient=request.user,
                recipient=recipient,
                start_date=start_date,
                end_date=end_date,
                ip_address=ip_address,
            )
            results.append({'channel': 'telegram', **result})

        if not results:
            return Response(
                {'detail': 'Alicinin bildirim kanali (email/telegram) yapilandirilmamis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_success = all(r.get('success') for r in results)
        return Response(
            {'results': results},
            status=status.HTTP_200_OK if all_success else status.HTTP_207_MULTI_STATUS,
        )

    @action(detail=False, methods=['get'], url_path='history')
    def share_history(self, request):
        """Get past report sharing records."""
        records = ReportShareRecord.objects.filter(
            patient=request.user,
        ).select_related('recipient')[:50]
        serializer = ReportShareRecordSerializer(records, many=True)
        return Response(serializer.data)


class RelativeDashboardViewSet(viewsets.ViewSet):
    """
    Read-only dashboard for patient relatives.
    Relatives can only view caregiver notes, daily assessments, and basic patient status.
    """
    permission_classes = [permissions.IsAuthenticated, IsRelative]

    def _get_patient(self, user):
        """Get the patient linked to this relative."""
        from apps.accounts.models import RelativeProfile
        try:
            profile = RelativeProfile.objects.select_related('patient').get(
                user=user, is_approved=True
            )
            return profile.patient
        except RelativeProfile.DoesNotExist:
            return None

    @action(detail=False, methods=['get'], url_path='patient')
    def patient_info(self, request):
        """Get basic info about the linked patient."""
        patient = self._get_patient(request.user)
        if not patient:
            return Response(
                {'detail': 'Onaylanmis hasta baglantiniz bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        today = date.today()
        week_ago = today - timedelta(days=7)

        # Latest cognitive score
        latest_score_obj = CognitiveScore.objects.filter(patient=patient).first()
        latest_score = latest_score_obj.overall_score if latest_score_obj else None

        # Today assessment
        today_assessment = DailyAssessment.objects.filter(
            patient=patient, assessment_date=today
        ).first()

        # Exercises this week
        exercises_this_week = ExerciseSession.objects.filter(
            patient=patient, started_at__date__gte=week_ago
        ).count()

        # Recent alerts (incidents in last week)
        recent_incidents = DailyAssessment.objects.filter(
            patient=patient,
            assessment_date__gte=week_ago,
        ).filter(
            Q(fall_occurred=True) | Q(wandering_occurred=True) | Q(medication_missed=True)
        ).count()

        data = {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'latest_score': latest_score,
            'exercises_this_week': exercises_this_week,
            'has_today_assessment': today_assessment is not None,
            'today_mood': today_assessment.mood_score if today_assessment else None,
            'recent_incidents': recent_incidents,
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='notes')
    def notes(self, request):
        """View caregiver notes for the linked patient (read-only)."""
        patient = self._get_patient(request.user)
        if not patient:
            return Response(
                {'detail': 'Onaylanmis hasta baglantiniz bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        notes = CaregiverNote.objects.filter(
            patient=patient
        ).order_by('-created_at')[:30]

        serializer = CaregiverNoteSerializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='assessments')
    def assessments(self, request):
        """View daily assessments for the linked patient (read-only)."""
        patient = self._get_patient(request.user)
        if not patient:
            return Response(
                {'detail': 'Onaylanmis hasta baglantiniz bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        month_ago = date.today() - timedelta(days=30)
        assessments = DailyAssessment.objects.filter(
            patient=patient,
            assessment_date__gte=month_ago,
        ).order_by('-assessment_date')[:30]

        serializer = DailyAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='alerts')
    def alerts(self, request):
        """View recent alerts for the linked patient."""
        patient = self._get_patient(request.user)
        if not patient:
            return Response(
                {'detail': 'Onaylanmis hasta baglantiniz bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        alerts = []
        week_ago = date.today() - timedelta(days=7)
        patient_name = patient.get_full_name()

        # Flagged notes
        flagged_notes = CaregiverNote.objects.filter(
            patient=patient,
            is_flagged_for_doctor=True,
            created_at__date__gte=week_ago,
        )
        for note in flagged_notes:
            alerts.append({
                'alert_type': 'flagged_note',
                'severity': note.severity,
                'patient_id': patient.id,
                'patient_name': patient_name,
                'message': f'{note.get_note_type_display()}: {note.title}',
                'timestamp': note.created_at,
                'related_id': str(note.id),
            })

        # Incident alerts
        recent_assessments = DailyAssessment.objects.filter(
            patient=patient,
            assessment_date__gte=week_ago,
        )
        for assessment in recent_assessments:
            if assessment.fall_occurred:
                alerts.append({
                    'alert_type': 'fall',
                    'severity': 3,
                    'patient_id': patient.id,
                    'patient_name': patient_name,
                    'message': f'Dusme olayi kaydedildi ({assessment.assessment_date})',
                    'timestamp': assessment.created_at,
                    'related_id': str(assessment.id),
                })
            if assessment.wandering_occurred:
                alerts.append({
                    'alert_type': 'wandering',
                    'severity': 3,
                    'patient_id': patient.id,
                    'patient_name': patient_name,
                    'message': f'Kaybolma/gezinme olayi ({assessment.assessment_date})',
                    'timestamp': assessment.created_at,
                    'related_id': str(assessment.id),
                })
            if assessment.medication_missed:
                alerts.append({
                    'alert_type': 'medication',
                    'severity': 2,
                    'patient_id': patient.id,
                    'patient_name': patient_name,
                    'message': f'Ilac atlama ({assessment.assessment_date})',
                    'timestamp': assessment.created_at,
                    'related_id': str(assessment.id),
                })

        alerts.sort(key=lambda a: -a['severity'])
        serializer = CaregiverAlertSerializer(alerts, many=True)
        return Response(serializer.data)
