"""
Social Media API Views.

Endpoint gruplari:
  1. SocialAccount CRUD
  2. SocialCampaign CRUD + workflow (generate, approve)
  3. SocialPost CRUD + workflow (approve, schedule, publish, retry)
  4. Bulk operations
  5. Calendar view
  6. Dashboard stats
  7. Image generation preview
"""

import logging
from datetime import datetime, timezone as dt_tz

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsDoctor

from .models import SocialAccount, SocialCampaign, SocialPost, PublishLog
from .serializers import (
    SocialAccountListSerializer,
    SocialAccountDetailSerializer,
    CreateSocialAccountSerializer,
    UpdateSocialAccountSerializer,
    SocialCampaignListSerializer,
    SocialCampaignDetailSerializer,
    CreateSocialCampaignSerializer,
    UpdateSocialCampaignSerializer,
    SocialPostListSerializer,
    SocialPostDetailSerializer,
    CreateSocialPostSerializer,
    UpdateSocialPostSerializer,
    BulkPostActionSerializer,
    CalendarPostSerializer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# 1) SOCIAL ACCOUNT ENDPOINTS
# =============================================================================

class SocialAccountListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/social/accounts/       — Hesap listesi
    POST /api/v1/social/accounts/       — Yeni hesap baglama
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return SocialAccount.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateSocialAccountSerializer
        return SocialAccountListSerializer

    def perform_create(self, serializer):
        serializer.save(connected_by=self.request.user)


class SocialAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/social/accounts/<id>/  — Hesap detay
    PATCH  /api/v1/social/accounts/<id>/  — Hesap guncelle
    DELETE /api/v1/social/accounts/<id>/  — Hesap sil
    """
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = SocialAccount.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UpdateSocialAccountSerializer
        return SocialAccountDetailSerializer


class SocialAccountValidateView(APIView):
    """
    POST /api/v1/social/accounts/<id>/validate/  — Token gecerliligi kontrol
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            account = SocialAccount.objects.get(pk=pk)
        except SocialAccount.DoesNotExist:
            return Response({'error': 'Hesap bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        from .publishers import get_publisher
        try:
            publisher = get_publisher(account)
            is_valid = publisher.validate_token()

            if is_valid:
                account.status = 'active'
                account.save(update_fields=['status'])
            else:
                account.status = 'expired'
                account.save(update_fields=['status'])

            return Response({
                'valid': is_valid,
                'status': account.status,
                'platform': account.platform,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAccountRefreshTokenView(APIView):
    """
    POST /api/v1/social/accounts/<id>/refresh-token/  — Token yenile
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            account = SocialAccount.objects.get(pk=pk)
        except SocialAccount.DoesNotExist:
            return Response({'error': 'Hesap bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        from .publishers import get_publisher
        from datetime import timedelta

        try:
            publisher = get_publisher(account)
            if not hasattr(publisher, 'refresh_token') or not callable(publisher.refresh_token):
                return Response(
                    {'error': f'{account.get_platform_display()} token yenileme desteklenmiyor'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_token = publisher.refresh_token()
            if new_token:
                account.access_token = new_token
                account.token_expires_at = timezone.now() + timedelta(days=60)
                account.status = 'active'
                account.save(update_fields=['access_token', 'token_expires_at', 'status'])
                return Response({'success': True, 'message': 'Token yenilendi'})
            else:
                return Response(
                    {'success': False, 'error': 'Token yenilenemedi'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# 2) SOCIAL CAMPAIGN ENDPOINTS
# =============================================================================

class SocialCampaignListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/social/campaigns/      — Kampanya listesi
    POST /api/v1/social/campaigns/      — Yeni kampanya olustur + pipeline baslar
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        qs = SocialCampaign.objects.all()

        # Filtreler
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        platform = self.request.query_params.get('platform')
        if platform:
            qs = qs.filter(platforms__contains=[platform])

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(theme__icontains=search))

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateSocialCampaignSerializer
        return SocialCampaignListSerializer

    def perform_create(self, serializer):
        campaign = serializer.save(
            created_by=self.request.user,
            status='generating',
        )

        # Pipeline'i baslat
        try:
            from .tasks import run_social_campaign_pipeline
            run_social_campaign_pipeline.delay(str(campaign.id))
        except Exception as e:
            logger.error(f"Social pipeline baslatma hatasi: {e}")
            campaign.status = 'draft'
            campaign.save(update_fields=['status'])


class SocialCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/social/campaigns/<id>/  — Kampanya detay
    PATCH  /api/v1/social/campaigns/<id>/  — Kampanya guncelle
    DELETE /api/v1/social/campaigns/<id>/  — Kampanya sil
    """
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = SocialCampaign.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UpdateSocialCampaignSerializer
        return SocialCampaignDetailSerializer


class SocialCampaignRegenerateView(APIView):
    """
    POST /api/v1/social/campaigns/<id>/regenerate/  — AI pipeline tekrar calistir
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            campaign = SocialCampaign.objects.get(pk=pk)
        except SocialCampaign.DoesNotExist:
            return Response({'error': 'Kampanya bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if campaign.status == 'generating':
            return Response(
                {'error': 'Pipeline zaten calisiyor'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mevcut draft postlari temizle
        campaign.posts.filter(status__in=['draft', 'review', 'generating']).delete()

        campaign.status = 'generating'
        campaign.content_output = {}
        campaign.schedule_output = {}
        campaign.save(update_fields=['status', 'content_output', 'schedule_output'])

        try:
            from .tasks import run_social_campaign_pipeline
            run_social_campaign_pipeline.delay(str(campaign.id))
        except Exception as e:
            logger.error(f"Social pipeline regenerate hatasi: {e}")
            campaign.status = 'draft'
            campaign.save(update_fields=['status'])

        return Response({'status': 'generating', 'message': 'Pipeline yeniden baslatildi'})


class SocialCampaignApproveAllView(APIView):
    """
    POST /api/v1/social/campaigns/<id>/approve-all/  — Tum postlari onayla
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            campaign = SocialCampaign.objects.get(pk=pk)
        except SocialCampaign.DoesNotExist:
            return Response({'error': 'Kampanya bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        updated = campaign.posts.filter(status='review').update(status='approved')
        campaign.status = 'approved'
        campaign.save(update_fields=['status'])

        return Response({
            'status': 'approved',
            'approved_count': updated,
        })


# =============================================================================
# 3) SOCIAL POST ENDPOINTS
# =============================================================================

class SocialPostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/social/posts/          — Post listesi
    POST /api/v1/social/posts/          — Yeni post olustur (manuel)
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        qs = SocialPost.objects.all().select_related('campaign', 'social_account')

        # Filtreler
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)

        platform = self.request.query_params.get('platform')
        if platform:
            qs = qs.filter(platform=platform)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(caption_tr__icontains=search) |
                Q(caption_en__icontains=search) |
                Q(edited_caption__icontains=search)
            )

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateSocialPostSerializer
        return SocialPostListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, ai_generated=False)


class SocialPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/social/posts/<id>/    — Post detay
    PATCH  /api/v1/social/posts/<id>/    — Post guncelle
    DELETE /api/v1/social/posts/<id>/    — Post sil
    """
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = SocialPost.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UpdateSocialPostSerializer
        return SocialPostDetailSerializer


class SocialPostApproveView(APIView):
    """
    POST /api/v1/social/posts/<id>/approve/  — Postu onayla
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            post = SocialPost.objects.get(pk=pk)
        except SocialPost.DoesNotExist:
            return Response({'error': 'Post bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if post.status not in ('review', 'draft'):
            return Response(
                {'error': f'Bu durumda onaylanamaz: {post.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post.status = 'approved'
        post.save(update_fields=['status'])

        # Kampanya durumunu guncelle
        self._update_campaign_status(post.campaign)

        return Response({'status': 'approved'})

    def _update_campaign_status(self, campaign):
        if not campaign:
            return
        stats = campaign.post_stats
        if stats['total'] > 0 and stats['total'] == stats['approved'] + stats['scheduled'] + stats['published']:
            campaign.status = 'approved'
        elif stats['approved'] > 0:
            campaign.status = 'partially_approved'
        campaign.save(update_fields=['status'])


class SocialPostScheduleView(APIView):
    """
    POST /api/v1/social/posts/<id>/schedule/  — Postu zamanla
    Body: { scheduled_at, social_account_id }
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            post = SocialPost.objects.get(pk=pk)
        except SocialPost.DoesNotExist:
            return Response({'error': 'Post bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if post.status not in ('approved', 'review', 'draft', 'failed'):
            return Response(
                {'error': f'Bu durumda zamanlanamaz: {post.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scheduled_at = request.data.get('scheduled_at')
        account_id = request.data.get('social_account_id')

        if not scheduled_at:
            return Response({'error': 'scheduled_at zorunlu'}, status=status.HTTP_400_BAD_REQUEST)

        if not account_id:
            return Response({'error': 'social_account_id zorunlu'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SocialAccount.objects.get(pk=account_id, platform=post.platform)
        except SocialAccount.DoesNotExist:
            return Response(
                {'error': 'Uygun sosyal hesap bulunamadi'},
                status=status.HTTP_404_NOT_FOUND,
            )

        post.scheduled_at = scheduled_at
        post.social_account = account
        post.status = 'scheduled'
        post.publish_error = ''
        post.save(update_fields=['scheduled_at', 'social_account', 'status', 'publish_error'])

        return Response({
            'status': 'scheduled',
            'scheduled_at': str(post.scheduled_at),
            'account': account.account_name,
        })


class SocialPostPublishNowView(APIView):
    """
    POST /api/v1/social/posts/<id>/publish-now/  — Hemen yayinla
    Body: { social_account_id }
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            post = SocialPost.objects.get(pk=pk)
        except SocialPost.DoesNotExist:
            return Response({'error': 'Post bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if post.status == 'published':
            return Response({'error': 'Post zaten yayinlanmis'}, status=status.HTTP_400_BAD_REQUEST)

        account_id = request.data.get('social_account_id') or (post.social_account_id if post.social_account else None)
        if not account_id:
            return Response({'error': 'social_account_id zorunlu'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SocialAccount.objects.get(pk=account_id, platform=post.platform)
        except SocialAccount.DoesNotExist:
            return Response({'error': 'Uygun sosyal hesap bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if not account.is_token_valid:
            return Response({'error': 'Token suresi dolmus'}, status=status.HTTP_400_BAD_REQUEST)

        post.social_account = account
        post.status = 'publishing'
        post.save(update_fields=['social_account', 'status'])

        from .publishers import get_publisher
        try:
            publisher = get_publisher(account)
            result = publisher.publish(post)

            PublishLog.objects.create(
                post=post,
                action='publish_now',
                success=result.success,
                response_data=result.response_data,
                error_message=result.error,
            )

            if result.success:
                post.status = 'published'
                post.published_at = timezone.now()
                post.platform_post_id = result.platform_post_id
                post.platform_url = result.platform_url
                post.publish_error = ''
                post.save(update_fields=[
                    'status', 'published_at', 'platform_post_id',
                    'platform_url', 'publish_error',
                ])

                account.total_posts_published += 1
                account.last_used_at = timezone.now()
                account.save(update_fields=['total_posts_published', 'last_used_at'])

                return Response({
                    'status': 'published',
                    'platform_url': result.platform_url,
                    'platform_post_id': result.platform_post_id,
                })
            else:
                post.status = 'failed'
                post.publish_error = result.error
                post.save(update_fields=['status', 'publish_error'])
                return Response(
                    {'error': result.error},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            post.status = 'failed'
            post.publish_error = str(e)
            post.save(update_fields=['status', 'publish_error'])
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialPostRetryView(APIView):
    """
    POST /api/v1/social/posts/<id>/retry/  — Basarisiz postu tekrar dene
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            post = SocialPost.objects.get(pk=pk)
        except SocialPost.DoesNotExist:
            return Response({'error': 'Post bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        if post.status != 'failed':
            return Response(
                {'error': 'Sadece basarisiz postlar icin retry yapilabilir'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from .tasks import retry_failed_post
            retry_failed_post.delay(str(post.id))
            return Response({'status': 'retrying', 'message': 'Post tekrar yayinlanacak'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# 4) BULK OPERATIONS
# =============================================================================

class BulkPostActionView(APIView):
    """
    POST /api/v1/social/posts/bulk-action/  — Toplu post islemi
    Body: { post_ids: [...], action: "approve"|"schedule"|"archive", ... }
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request):
        serializer = BulkPostActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_ids = serializer.validated_data['post_ids']
        action = serializer.validated_data['action']
        posts = SocialPost.objects.filter(id__in=post_ids)

        results = {'updated': 0, 'skipped': 0, 'errors': []}

        for post in posts:
            try:
                if action == 'approve':
                    if post.status in ('review', 'draft'):
                        post.status = 'approved'
                        post.save(update_fields=['status'])
                        results['updated'] += 1
                    else:
                        results['skipped'] += 1

                elif action == 'schedule':
                    if post.status in ('approved', 'review', 'draft'):
                        account_id = serializer.validated_data.get('social_account_id')
                        scheduled_at = serializer.validated_data.get('scheduled_at')
                        try:
                            account = SocialAccount.objects.get(pk=account_id, platform=post.platform)
                            post.social_account = account
                            post.scheduled_at = scheduled_at or timezone.now()
                            post.status = 'scheduled'
                            post.save(update_fields=['social_account', 'scheduled_at', 'status'])
                            results['updated'] += 1
                        except SocialAccount.DoesNotExist:
                            results['errors'].append(f'{post.id}: Uygun hesap yok')
                            results['skipped'] += 1
                    else:
                        results['skipped'] += 1

                elif action == 'archive':
                    post.status = 'archived'
                    post.save(update_fields=['status'])
                    results['updated'] += 1

            except Exception as e:
                results['errors'].append(f'{post.id}: {str(e)}')

        return Response(results)


# =============================================================================
# 5) CALENDAR VIEW
# =============================================================================

class SocialCalendarView(APIView):
    """
    GET /api/v1/social/calendar/?month=2026-03  — Takvim gorunumu
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        month_str = request.query_params.get('month')

        if month_str:
            try:
                year, month = map(int, month_str.split('-'))
            except (ValueError, AttributeError):
                return Response(
                    {'error': 'Gecersiz ay formati. Ornek: 2026-03'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            now = timezone.now()
            year, month = now.year, now.month

        # Ayin baslangic ve bitis tarihleri
        start_date = datetime(year, month, 1, tzinfo=dt_tz.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=dt_tz.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=dt_tz.utc)

        posts = SocialPost.objects.filter(
            scheduled_at__gte=start_date,
            scheduled_at__lt=end_date,
        ).exclude(
            status='archived'
        ).select_related('campaign').order_by('scheduled_at')

        platform = request.query_params.get('platform')
        if platform:
            posts = posts.filter(platform=platform)

        serializer = CalendarPostSerializer(posts, many=True)
        return Response({
            'year': year,
            'month': month,
            'posts': serializer.data,
        })


# =============================================================================
# 6) DASHBOARD STATS
# =============================================================================

class SocialDashboardStatsView(APIView):
    """
    GET /api/v1/social/dashboard/  — Dashboard istatistikleri
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        accounts = SocialAccount.objects.all()
        campaigns = SocialCampaign.objects.all()
        posts = SocialPost.objects.all()

        # Platform bazli post sayilari
        platform_counts = {}
        for choice in SocialPost.PLATFORM_CHOICES:
            platform_counts[choice[0]] = posts.filter(platform=choice[0]).count()

        data = {
            'total_accounts': accounts.count(),
            'active_accounts': accounts.filter(status='active').count(),
            'expired_accounts': accounts.filter(status='expired').count(),
            'total_campaigns': campaigns.count(),
            'active_campaigns': campaigns.exclude(status__in=['completed', 'archived']).count(),
            'total_posts': posts.count(),
            'published_posts': posts.filter(status='published').count(),
            'scheduled_posts': posts.filter(status='scheduled').count(),
            'failed_posts': posts.filter(status='failed').count(),
            'posts_by_platform': platform_counts,
            'total_tokens_used': campaigns.aggregate(t=Sum('total_tokens'))['t'] or 0,
        }

        return Response(data)


# =============================================================================
# 7) IMAGE GENERATION PREVIEW
# =============================================================================

class ImagePreviewView(APIView):
    """
    POST /api/v1/social/image-preview/  — Gorsel onizleme (base64)
    Body: {
        template: "info_card" | "stat_card" | "quote_card",
        platform: "instagram" | "linkedin",
        ...template-specific fields...
    }
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request):
        import base64
        from .image_generator import SocialImageGenerator

        template = request.data.get('template', 'info_card')
        platform = request.data.get('platform', 'instagram')

        gen = SocialImageGenerator()

        try:
            if template == 'info_card':
                img_bytes = gen.info_card(
                    title=request.data.get('title', ''),
                    items=request.data.get('items', []),
                    platform=platform,
                    subtitle=request.data.get('subtitle', ''),
                )
            elif template == 'stat_card':
                img_bytes = gen.stat_card(
                    stat_value=request.data.get('stat_value', ''),
                    stat_label=request.data.get('stat_label', ''),
                    description=request.data.get('description', ''),
                    platform=platform,
                    source=request.data.get('source', ''),
                )
            elif template == 'quote_card':
                img_bytes = gen.quote_card(
                    quote=request.data.get('quote', ''),
                    author=request.data.get('author', ''),
                    platform=platform,
                )
            else:
                return Response(
                    {'error': f'Bilinmeyen sablon: {template}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            b64 = base64.b64encode(img_bytes).decode('utf-8')
            return Response({
                'image': f'data:image/png;base64,{b64}',
                'template': template,
                'platform': platform,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageTemplatesView(APIView):
    """
    GET /api/v1/social/image-templates/  — Mevcut gorsel sablonlari
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        from .image_generator import SocialImageGenerator

        gen = SocialImageGenerator()
        return Response({
            'templates': gen.get_available_templates(),
            'sizes': gen.get_available_sizes(),
        })
