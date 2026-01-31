from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import (
    CognitiveExercise,
    ExerciseSession,
    DailyAssessment,
    CaregiverNote,
    CognitiveScore,
)
from .serializers import (
    CognitiveExerciseSerializer,
    ExerciseSessionSerializer,
    ExerciseSessionCreateSerializer,
    DailyAssessmentSerializer,
    CaregiverNoteSerializer,
    CognitiveScoreSerializer,
    CognitiveStatsSerializer,
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


class DailyAssessmentViewSet(viewsets.ModelViewSet):
    """
    Daily cognitive and functional assessments.
    """
    serializer_class = DailyAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
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
    For now, patients can see their own notes.
    """
    serializer_class = CaregiverNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
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
