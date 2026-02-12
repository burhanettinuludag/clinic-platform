from datetime import date, timedelta
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import SeizureEvent, EpilepsyTrigger
from .serializers import (
    SeizureEventSerializer,
    SeizureEventListSerializer,
    EpilepsyTriggerSerializer,
    SeizureStatsSerializer,
)


class SeizureEventViewSet(viewsets.ModelViewSet):
    """Seizure event diary."""
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['seizure_type']

    def get_serializer_class(self):
        if self.action == 'list':
            return SeizureEventListSerializer
        return SeizureEventSerializer

    def get_queryset(self):
        qs = SeizureEvent.objects.filter(patient=self.request.user)
        start = self.request.query_params.get('start_date')
        end = self.request.query_params.get('end_date')
        if start:
            qs = qs.filter(seizure_datetime__date__gte=start)
        if end:
            qs = qs.filter(seizure_datetime__date__lte=end)
        return qs.prefetch_related('triggers_identified')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get seizure statistics."""
        qs = SeizureEvent.objects.filter(patient=request.user)
        today = date.today()
        month_start = today.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        total = qs.count()
        aggregates = qs.aggregate(
            avg_intensity=Avg('intensity'),
            avg_duration=Avg('duration_seconds'),
        )

        seizures_this_month = qs.filter(seizure_datetime__date__gte=month_start).count()
        seizures_last_month = qs.filter(
            seizure_datetime__date__gte=last_month_start,
            seizure_datetime__date__lt=month_start,
        ).count()

        triggers = (
            EpilepsyTrigger.objects
            .filter(seizure_events__patient=request.user)
            .annotate(count=Count('seizure_events'))
            .order_by('-count')[:5]
        )
        most_common_triggers = [
            {'name': t.name_tr, 'count': t.count} for t in triggers
        ]

        seizure_type = (
            qs.values('seizure_type')
            .annotate(count=Count('id'))
            .order_by('-count')
            .first()
        )
        most_common_type = seizure_type['seizure_type'] if seizure_type else ''

        with_loss = qs.filter(loss_of_consciousness=True).count()
        consciousness_pct = (with_loss / total * 100) if total > 0 else 0

        data = {
            'total_seizures': total,
            'avg_intensity': round(aggregates['avg_intensity'] or 0, 1),
            'avg_duration': round(aggregates['avg_duration'] or 0, 0),
            'seizures_this_month': seizures_this_month,
            'seizures_last_month': seizures_last_month,
            'most_common_triggers': most_common_triggers,
            'most_common_type': most_common_type,
            'consciousness_loss_percentage': round(consciousness_pct, 1),
        }
        serializer = SeizureStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Monthly seizure frequency for charting."""
        months = int(request.query_params.get('months', 6))
        today = date.today()
        start = today - timedelta(days=months * 30)

        qs = self.get_queryset().filter(seizure_datetime__date__gte=start)
        data = []
        current = start.replace(day=1)
        while current <= today:
            next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            count = qs.filter(
                seizure_datetime__date__gte=current,
                seizure_datetime__date__lt=next_month,
            ).count()
            avg_int = qs.filter(
                seizure_datetime__date__gte=current,
                seizure_datetime__date__lt=next_month,
            ).aggregate(avg=Avg('intensity'))['avg']
            data.append({
                'month': current.strftime('%Y-%m'),
                'count': count,
                'avg_intensity': round(avg_int or 0, 1),
            })
            current = next_month

        return Response(data)


class EpilepsyTriggerViewSet(viewsets.ModelViewSet):
    """Epilepsy triggers - predefined + custom."""
    serializer_class = EpilepsyTriggerSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_predefined']

    def get_queryset(self):
        return EpilepsyTrigger.objects.filter(
            Q(is_predefined=True) | Q(created_by=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_predefined=False)

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """Analyze trigger frequency from patient's seizures."""
        triggers = (
            EpilepsyTrigger.objects
            .filter(seizure_events__patient=request.user)
            .annotate(seizure_count=Count('seizure_events'))
            .order_by('-seizure_count')
        )
        data = [
            {
                'id': str(t.id),
                'name_tr': t.name_tr,
                'name_en': t.name_en,
                'category': t.category,
                'seizure_count': t.seizure_count,
            }
            for t in triggers
        ]
        return Response(data)
