from datetime import date, timedelta
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import DiseaseModule, PatientModule, TaskTemplate, TaskCompletion
from .serializers import (
    DiseaseModuleSerializer,
    PatientModuleSerializer,
    TaskTemplateSerializer,
    TaskCompletionSerializer,
)


class DiseaseModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """Public listing of disease modules."""
    queryset = DiseaseModule.objects.filter(is_active=True)
    serializer_class = DiseaseModuleSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class PatientModuleViewSet(viewsets.ModelViewSet):
    """Patient's enrolled modules."""
    serializer_class = PatientModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return PatientModule.objects.filter(
            patient=self.request.user
        ).select_related('disease_module')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active enrolled modules."""
        qs = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TaskTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """Task templates for enrolled modules."""
    serializer_class = TaskTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['disease_module', 'task_type', 'frequency']

    def get_queryset(self):
        enrolled_module_ids = PatientModule.objects.filter(
            patient=self.request.user, is_active=True
        ).values_list('disease_module_id', flat=True)
        return TaskTemplate.objects.filter(
            disease_module_id__in=enrolled_module_ids, is_active=True
        )

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's tasks (daily + weekly on correct day)."""
        qs = self.get_queryset()
        today_weekday = date.today().weekday()
        daily = qs.filter(frequency='daily')
        weekly = qs.filter(frequency='weekly')

        completed_today = TaskCompletion.objects.filter(
            patient=request.user,
            completed_date=date.today(),
        ).values_list('task_template_id', flat=True)

        tasks = daily | weekly
        serializer = self.get_serializer(tasks, many=True)
        data = serializer.data
        for item in data:
            item['is_completed_today'] = item['id'] in list(map(str, completed_today))
        return Response(data)

    @action(detail=False, methods=['get'])
    def week(self, request):
        """Get this week's tasks with completion status."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        qs = self.get_queryset()
        completions = TaskCompletion.objects.filter(
            patient=request.user,
            completed_date__gte=week_start,
            completed_date__lte=week_end,
        )

        serializer = self.get_serializer(qs, many=True)
        data = serializer.data

        completion_map = {}
        for c in completions:
            key = str(c.task_template_id)
            if key not in completion_map:
                completion_map[key] = []
            completion_map[key].append(str(c.completed_date))

        for item in data:
            item['completions_this_week'] = completion_map.get(item['id'], [])

        return Response(data)


class TaskCompletionViewSet(viewsets.ModelViewSet):
    """Patient task completions."""
    serializer_class = TaskCompletionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task_template', 'completed_date']

    def get_queryset(self):
        return TaskCompletion.objects.filter(
            patient=self.request.user
        ).select_related('task_template')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get completion stats for the patient."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        qs = self.get_queryset()
        total = qs.count()
        this_week = qs.filter(completed_date__gte=week_start).count()
        this_month = qs.filter(completed_date__gte=month_start).count()
        today_count = qs.filter(completed_date=today).count()

        # Streak calculation
        streak = 0
        check_date = today
        while True:
            if qs.filter(completed_date=check_date).exists():
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return Response({
            'total_completions': total,
            'completed_today': today_count,
            'completed_this_week': this_week,
            'completed_this_month': this_month,
            'current_streak': streak,
        })
