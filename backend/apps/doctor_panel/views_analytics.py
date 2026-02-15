"""
Doctor Analytics API.
GET /api/v1/doctor/analytics/overview/
GET /api/v1/doctor/analytics/content-stats/
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsDoctor


class AnalyticsOverviewView(APIView):
    """Genel istatistik ozeti."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        from apps.content.models import Article, NewsArticle
        from apps.accounts.models import DoctorAuthor

        user = request.user
        now = timezone.now()
        last_30 = now - timedelta(days=30)
        last_7 = now - timedelta(days=7)

        # Yazar profili
        try:
            da = DoctorAuthor.objects.get(doctor__user=user)
            da_id = da.id
        except DoctorAuthor.DoesNotExist:
            da_id = None

        # Makale istatistikleri
        art_qs = Article.objects.filter(
            Q(author=user) | Q(doctor_author_id=da_id)
        ) if da_id else Article.objects.filter(author=user)

        news_qs = NewsArticle.objects.filter(author_id=da_id) if da_id else NewsArticle.objects.none()

        total_articles = art_qs.count()
        published_articles = art_qs.filter(status='published').count()
        draft_articles = art_qs.filter(status='draft').count()
        review_articles = art_qs.filter(status='review').count()

        total_news = news_qs.count()
        published_news = news_qs.filter(status='published').count()

        total_views = (
            art_qs.aggregate(s=Sum('view_count'))['s'] or 0
        ) + (
            news_qs.aggregate(s=Sum('view_count'))['s'] or 0
        )

        avg_rating = art_qs.filter(
            average_rating__gt=0
        ).aggregate(a=Avg('average_rating'))['a'] or 0

        # Son 30 gun yayinlanan
        recent_published = art_qs.filter(
            published_at__gte=last_30, status='published'
        ).count() + news_qs.filter(
            published_at__gte=last_30, status='published'
        ).count()

        return Response({
            'articles': {
                'total': total_articles,
                'published': published_articles,
                'draft': draft_articles,
                'review': review_articles,
            },
            'news': {
                'total': total_news,
                'published': published_news,
            },
            'total_views': total_views,
            'avg_rating': round(avg_rating, 1),
            'recent_published_30d': recent_published,
        })


class ContentStatsView(APIView):
    """Zaman bazli icerik istatistikleri (grafik icin)."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        from apps.content.models import Article, NewsArticle
        from apps.accounts.models import DoctorAuthor

        user = request.user
        period = request.query_params.get('period', '6months')

        if period == '12months':
            start = timezone.now() - timedelta(days=365)
        elif period == '3months':
            start = timezone.now() - timedelta(days=90)
        else:
            start = timezone.now() - timedelta(days=180)

        try:
            da = DoctorAuthor.objects.get(doctor__user=user)
            da_id = da.id
        except DoctorAuthor.DoesNotExist:
            da_id = None

        art_qs = Article.objects.filter(
            Q(author=user) | Q(doctor_author_id=da_id)
        ) if da_id else Article.objects.filter(author=user)

        news_qs = NewsArticle.objects.filter(author_id=da_id) if da_id else NewsArticle.objects.none()

        # Aylik yayinlanan makale
        articles_by_month = list(
            art_qs.filter(
                published_at__gte=start, status='published'
            ).annotate(
                month=TruncMonth('published_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
        )

        # Aylik yayinlanan haber
        news_by_month = list(
            news_qs.filter(
                published_at__gte=start, status='published'
            ).annotate(
                month=TruncMonth('published_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
        )

        # Gunluk goruntulenme (son 30 gun)
        views_by_day = list(
            art_qs.filter(
                published_at__gte=timezone.now() - timedelta(days=30),
                status='published',
            ).annotate(
                day=TruncDate('published_at')
            ).values('day').annotate(
                views=Sum('view_count')
            ).order_by('day')
        )

        # Status dagilimi
        status_dist = list(
            art_qs.values('status').annotate(count=Count('id')).order_by('status')
        )

        def fmt(items, key='month'):
            return [{'date': item[key].isoformat() if item[key] else '', 'count': item.get('count', item.get('views', 0))} for item in items]

        return Response({
            'articles_by_month': fmt(articles_by_month),
            'news_by_month': fmt(news_by_month),
            'views_by_day': fmt(views_by_day, 'day'),
            'status_distribution': status_dist,
        })
