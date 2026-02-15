from django.utils import timezone
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminUser
from .models import SiteConfig, FeatureFlag, Announcement, HomepageHero, SocialLink
from .serializers_site import (
    SiteConfigSerializer, SiteConfigPublicSerializer,
    FeatureFlagSerializer, FeatureFlagPublicSerializer,
    AnnouncementSerializer, HomepageHeroSerializer, SocialLinkSerializer,
)


# ============================
# PUBLIC ENDPOINTS
# ============================

class PublicSiteConfigView(generics.ListAPIView):
    """is_public=True olan SiteConfig degerlerini dondurur."""
    serializer_class = SiteConfigPublicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        return SiteConfig.objects.filter(is_public=True)


class ActiveAnnouncementsView(generics.ListAPIView):
    """Aktif ve tarih araliginda olan duyurulari dondurur."""
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        qs = Announcement.objects.filter(is_active=True)
        qs = qs.exclude(starts_at__gt=now)
        qs = qs.exclude(expires_at__lt=now)
        return qs


class ActiveHeroView(generics.ListAPIView):
    """Aktif hero section verisini dondurur."""
    serializer_class = HomepageHeroSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        return HomepageHero.objects.filter(is_active=True)[:1]


class PublicSocialLinksView(generics.ListAPIView):
    """Aktif sosyal medya linklerini dondurur."""
    serializer_class = SocialLinkSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        return SocialLink.objects.filter(is_active=True)


class PublicFeatureFlagsView(generics.ListAPIView):
    """Public feature flag durumlarini dondurur."""
    serializer_class = FeatureFlagPublicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None

    def get_queryset(self):
        return FeatureFlag.objects.all()


# ============================
# ADMIN ENDPOINTS
# ============================

class AdminSiteConfigViewSet(viewsets.ModelViewSet):
    queryset = SiteConfig.objects.all()
    serializer_class = SiteConfigSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None


class AdminFeatureFlagViewSet(viewsets.ModelViewSet):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None


class AdminAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None


class AdminHomepageHeroViewSet(viewsets.ModelViewSet):
    queryset = HomepageHero.objects.all()
    serializer_class = HomepageHeroSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None


class AdminSocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None


# ============================
# DASHBOARD STATS
# ============================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_stats_view(request):
    """Site yonetim paneli istatistikleri."""
    from django.contrib.auth import get_user_model
    from datetime import timedelta

    User = get_user_model()
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    total_users = User.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_doctors = User.objects.filter(role='doctor').count()
    new_users_today = User.objects.filter(date_joined__gte=today_start).count()
    new_users_this_week = User.objects.filter(date_joined__gte=week_ago).count()

    # Content stats
    total_articles = 0
    published_articles = 0
    pending_review = 0
    total_news = 0
    try:
        from apps.content.models import NewsArticle
        total_news = NewsArticle.objects.count()
        published_articles = NewsArticle.objects.filter(status='published').count()
        pending_review = NewsArticle.objects.filter(status='review').count()
        total_articles = total_news
    except Exception:
        pass

    active_announcements = Announcement.objects.filter(is_active=True).count()
    feature_flags_on = FeatureFlag.objects.filter(is_enabled=True).count()
    feature_flags_off = FeatureFlag.objects.filter(is_enabled=False).count()

    return Response({
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'new_users_today': new_users_today,
        'new_users_this_week': new_users_this_week,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'pending_review': pending_review,
        'total_news': total_news,
        'active_announcements': active_announcements,
        'feature_flags_on': feature_flags_on,
        'feature_flags_off': feature_flags_off,
    })
