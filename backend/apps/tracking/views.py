from datetime import date, timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import SymptomDefinition, SymptomEntry, Medication, MedicationLog, ReminderConfig
from .serializers import (
    SymptomDefinitionSerializer,
    SymptomEntrySerializer,
    MedicationSerializer,
    MedicationLogSerializer,
    ReminderConfigSerializer,
)


class SymptomDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """Symptom definitions for enrolled modules."""
    serializer_class = SymptomDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['disease_module', 'input_type']

    def get_queryset(self):
        from apps.patients.models import PatientModule
        enrolled_module_ids = PatientModule.objects.filter(
            patient=self.request.user, is_active=True
        ).values_list('disease_module_id', flat=True)
        return SymptomDefinition.objects.filter(
            disease_module_id__in=enrolled_module_ids, is_active=True
        )


class SymptomEntryViewSet(viewsets.ModelViewSet):
    """Patient symptom entries."""
    serializer_class = SymptomEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['symptom_definition', 'recorded_date']

    def get_queryset(self):
        return SymptomEntry.objects.filter(
            patient=self.request.user
        ).select_related('symptom_definition')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def chart(self, request):
        """Get symptom data for charting (last 30 days)."""
        days = int(request.query_params.get('days', 30))
        symptom_id = request.query_params.get('symptom_definition')
        start_date = date.today() - timedelta(days=days)

        qs = self.get_queryset().filter(recorded_date__gte=start_date)
        if symptom_id:
            qs = qs.filter(symptom_definition_id=symptom_id)

        qs = qs.order_by('recorded_date')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's symptom entries."""
        qs = self.get_queryset().filter(recorded_date=date.today())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class MedicationViewSet(viewsets.ModelViewSet):
    """Patient medications CRUD."""
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_queryset(self):
        return Medication.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active medications."""
        qs = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class MedicationLogViewSet(viewsets.ModelViewSet):
    """Medication intake logs."""
    serializer_class = MedicationLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medication', 'was_taken']

    def get_queryset(self):
        return MedicationLog.objects.filter(
            patient=self.request.user
        ).select_related('medication')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's medication logs."""
        qs = self.get_queryset().filter(taken_at__date=date.today())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def adherence(self, request):
        """Calculate medication adherence rate (last 30 days)."""
        start_date = date.today() - timedelta(days=30)
        qs = self.get_queryset().filter(taken_at__date__gte=start_date)
        total = qs.count()
        taken = qs.filter(was_taken=True).count()
        rate = (taken / total * 100) if total > 0 else 0
        return Response({
            'total_logs': total,
            'taken': taken,
            'missed': total - taken,
            'adherence_rate': round(rate, 1),
        })


class ReminderConfigViewSet(viewsets.ModelViewSet):
    """Patient reminder configurations."""
    serializer_class = ReminderConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_queryset(self):
        return ReminderConfig.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
