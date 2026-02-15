"""
Marketing Campaign API Views.

Doktor panelinden kampanya olusturma, listeleme, duzenleme, onaylama.
"""

import logging
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsDoctor
from apps.common.models import MarketingCampaign
from .serializers_marketing import (
    MarketingCampaignListSerializer,
    MarketingCampaignDetailSerializer,
    CreateMarketingCampaignSerializer,
    UpdateMarketingCampaignSerializer,
)

logger = logging.getLogger(__name__)


class MarketingCampaignListCreateView(generics.ListCreateAPIView):
    """Kampanya listesi ve yeni kampanya baslatma."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return MarketingCampaign.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMarketingCampaignSerializer
        return MarketingCampaignListSerializer

    def perform_create(self, serializer):
        campaign = serializer.save(
            created_by=self.request.user,
            status='generating',
        )

        # Pipeline'i async baslat (Celery task olarak)
        try:
            from apps.doctor_panel.tasks import run_marketing_pipeline
            run_marketing_pipeline.delay(str(campaign.id))
        except Exception as e:
            logger.error(f"Marketing pipeline baslatilamadi: {e}")
            campaign.status = 'review'
            campaign.editor_notes = f"Pipeline baslatilamadi: {str(e)}"
            campaign.save(update_fields=['status', 'editor_notes'])

        return campaign


class MarketingCampaignDetailView(generics.RetrieveUpdateAPIView):
    """Kampanya detayi ve duzenleme."""
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = MarketingCampaign.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UpdateMarketingCampaignSerializer
        return MarketingCampaignDetailSerializer


class MarketingCampaignApproveView(APIView):
    """Kampanya onaylama."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            campaign = MarketingCampaign.objects.get(pk=pk)
        except MarketingCampaign.DoesNotExist:
            return Response(
                {'error': 'Kampanya bulunamadi'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if campaign.status != 'review':
            return Response(
                {'error': 'Sadece inceleme durumundaki kampanyalar onaylanabilir'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign.status = 'approved'
        campaign.approved_at = timezone.now()
        campaign.save(update_fields=['status', 'approved_at'])

        return Response({'status': 'approved'})


class MarketingCampaignRegenerateView(APIView):
    """Kampanya icerigini tekrar uret."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            campaign = MarketingCampaign.objects.get(pk=pk)
        except MarketingCampaign.DoesNotExist:
            return Response(
                {'error': 'Kampanya bulunamadi'},
                status=status.HTTP_404_NOT_FOUND,
            )

        campaign.status = 'generating'
        campaign.content_output = {}
        campaign.visual_briefs = {}
        campaign.schedule = {}
        campaign.save(update_fields=[
            'status', 'content_output', 'visual_briefs', 'schedule',
        ])

        try:
            from apps.doctor_panel.tasks import run_marketing_pipeline
            run_marketing_pipeline.delay(str(campaign.id))
        except Exception as e:
            logger.error(f"Marketing pipeline yeniden baslatilamadi: {e}")
            campaign.status = 'review'
            campaign.editor_notes = f"Yeniden uretim hatasi: {str(e)}"
            campaign.save(update_fields=['status', 'editor_notes'])

        return Response({'status': 'regenerating'})
