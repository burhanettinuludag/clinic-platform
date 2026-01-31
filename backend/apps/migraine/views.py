from datetime import date, timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import MigraineAttack, MigraineTrigger
from .serializers import (
    MigraineAttackSerializer,
    MigraineAttackListSerializer,
    MigraineTriggerSerializer,
    MigraineStatsSerializer,
)
from .reports import MigraineReportGenerator


class MigraineAttackViewSet(viewsets.ModelViewSet):
    """Migraine attack diary."""
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pain_location', 'has_aura']

    def get_serializer_class(self):
        if self.action == 'list':
            return MigraineAttackListSerializer
        return MigraineAttackSerializer

    def get_queryset(self):
        qs = MigraineAttack.objects.filter(patient=self.request.user)
        start = self.request.query_params.get('start_date')
        end = self.request.query_params.get('end_date')
        if start:
            qs = qs.filter(start_datetime__date__gte=start)
        if end:
            qs = qs.filter(start_datetime__date__lte=end)
        return qs.prefetch_related('triggers_identified')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get migraine statistics."""
        qs = MigraineAttack.objects.filter(patient=request.user)
        today = date.today()
        month_start = today.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        total = qs.count()
        aggregates = qs.aggregate(
            avg_intensity=Avg('intensity'),
            avg_duration=Avg('duration_minutes'),
        )

        attacks_this_month = qs.filter(start_datetime__date__gte=month_start).count()
        attacks_last_month = qs.filter(
            start_datetime__date__gte=last_month_start,
            start_datetime__date__lt=month_start,
        ).count()

        # Most common triggers
        triggers = (
            MigraineTrigger.objects
            .filter(attacks__patient=request.user)
            .annotate(count=Count('attacks'))
            .order_by('-count')[:5]
        )
        most_common_triggers = [
            {'name': t.name_tr, 'count': t.count} for t in triggers
        ]

        # Most common pain location
        location = (
            qs.exclude(pain_location='')
            .values('pain_location')
            .annotate(count=Count('id'))
            .order_by('-count')
            .first()
        )
        most_common_location = location['pain_location'] if location else ''

        # Aura percentage
        with_aura = qs.filter(has_aura=True).count()
        aura_pct = (with_aura / total * 100) if total > 0 else 0

        data = {
            'total_attacks': total,
            'avg_intensity': round(aggregates['avg_intensity'] or 0, 1),
            'avg_duration': round(aggregates['avg_duration'] or 0, 0),
            'attacks_this_month': attacks_this_month,
            'attacks_last_month': attacks_last_month,
            'most_common_triggers': most_common_triggers,
            'most_common_location': most_common_location,
            'aura_percentage': round(aura_pct, 1),
        }
        serializer = MigraineStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Monthly attack frequency for charting."""
        months = int(request.query_params.get('months', 6))
        today = date.today()
        start = today - timedelta(days=months * 30)

        qs = self.get_queryset().filter(start_datetime__date__gte=start)
        data = []
        current = start.replace(day=1)
        while current <= today:
            next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            count = qs.filter(
                start_datetime__date__gte=current,
                start_datetime__date__lt=next_month,
            ).count()
            avg_int = qs.filter(
                start_datetime__date__gte=current,
                start_datetime__date__lt=next_month,
            ).aggregate(avg=Avg('intensity'))['avg']
            data.append({
                'month': current.strftime('%Y-%m'),
                'count': count,
                'avg_intensity': round(avg_int or 0, 1),
            })
            current = next_month

        return Response(data)

    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate PDF report for doctor visits."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = date.fromisoformat(start_date)
        if end_date:
            end_date = date.fromisoformat(end_date)

        generator = MigraineReportGenerator(
            user=request.user,
            start_date=start_date,
            end_date=end_date
        )

        pdf_content = generator.generate()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f'migraine_report_{timezone.now().strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


class MigraineTriggerViewSet(viewsets.ModelViewSet):
    """Migraine triggers - predefined + custom."""
    serializer_class = MigraineTriggerSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_predefined']

    def get_queryset(self):
        return MigraineTrigger.objects.filter(
            Q(is_predefined=True) | Q(created_by=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_predefined=False)

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """Analyze trigger frequency from patient's attacks."""
        triggers = (
            MigraineTrigger.objects
            .filter(attacks__patient=request.user)
            .annotate(attack_count=Count('attacks'))
            .order_by('-attack_count')
        )
        data = [
            {
                'id': str(t.id),
                'name_tr': t.name_tr,
                'name_en': t.name_en,
                'category': t.category,
                'attack_count': t.attack_count,
            }
            for t in triggers
        ]
        return Response(data)
