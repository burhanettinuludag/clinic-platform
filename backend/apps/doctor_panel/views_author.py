"""
Yazar (DoctorAuthor) islemleri view'lari.

Endpoint'ler:
─────────────────────────────────────────────
YAZAR PROFİL
  POST   /api/v1/doctor/author/profile/          → Yazar profili olustur
  GET    /api/v1/doctor/author/profile/          → Kendi profilini gor
  PATCH  /api/v1/doctor/author/profile/          → Profilini guncelle

MAKALE (Article) YÖNETİMİ
  GET    /api/v1/doctor/author/articles/          → Makalelerimi listele
  POST   /api/v1/doctor/author/articles/          → Yeni makale olustur
  GET    /api/v1/doctor/author/articles/<id>/     → Makale detay
  PATCH  /api/v1/doctor/author/articles/<id>/     → Makale duzenle
  DELETE /api/v1/doctor/author/articles/<id>/     → Makale sil (sadece draft)
  POST   /api/v1/doctor/author/articles/<id>/transition/  → Durum gecisi
  POST   /api/v1/doctor/author/articles/<id>/run-pipeline/ → Pipeline calistir

HABER (NewsArticle) YÖNETİMİ
  GET    /api/v1/doctor/author/news/              → Haberlerimi listele
  POST   /api/v1/doctor/author/news/              → Yeni haber olustur
  GET    /api/v1/doctor/author/news/<id>/         → Haber detay
  PATCH  /api/v1/doctor/author/news/<id>/         → Haber duzenle
  DELETE /api/v1/doctor/author/news/<id>/         → Haber sil (sadece draft)
  POST   /api/v1/doctor/author/news/<id>/transition/ → Durum gecisi

İSTATİSTİKLER
  GET    /api/v1/doctor/author/stats/             → Yazar istatistikleri
"""

import logging

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Q

from apps.accounts.models import DoctorAuthor
from apps.accounts.permissions import IsDoctor
from apps.content.models import Article, NewsArticle, ArticleReview
from .serializers_author import (
    DoctorAuthorListSerializer,
    DoctorAuthorDetailSerializer,
    DoctorAuthorCreateSerializer,
    AuthorArticleListSerializer,
    AuthorArticleDetailSerializer,
    AuthorArticleCreateSerializer,
    AuthorNewsListSerializer,
    AuthorNewsDetailSerializer,
    AuthorNewsCreateSerializer,
    ArticleReviewSerializer,
    ArticleStatusTransitionSerializer,
    NewsStatusTransitionSerializer,
)
from apps.notifications.content_notifications import (
    notify_article_transition,
    notify_news_transition,
    notify_pipeline_result,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# HELPER: Yazar profili al (veya 404)
# ═══════════════════════════════════════════════

def _get_author_or_none(user):
    """Kullanicinin DoctorAuthor profilini dondur, yoksa None."""
    try:
        return user.doctor_profile.author_profile
    except Exception:
        return None


# ═══════════════════════════════════════════════
# 1. YAZAR PROFİL
# ═══════════════════════════════════════════════

class AuthorProfileView(views.APIView):
    """
    Yazar profili CRUD.
    GET  → profilimi gor
    POST → yeni profil olustur
    PATCH → profilimi guncelle
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        author = _get_author_or_none(request.user)
        if not author:
            return Response(
                {'detail': 'Yazar profiliniz bulunmuyor. POST ile olusturabilirsiniz.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DoctorAuthorDetailSerializer(author)
        return Response(serializer.data)

    def post(self, request):
        serializer = DoctorAuthorCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        author = serializer.save()
        return Response(
            DoctorAuthorDetailSerializer(author).data,
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        author = _get_author_or_none(request.user)
        if not author:
            return Response(
                {'detail': 'Yazar profiliniz bulunmuyor.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DoctorAuthorDetailSerializer(
            author,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ═══════════════════════════════════════════════
# 2. MAKALE (Article) YÖNETİMİ
# ═══════════════════════════════════════════════

class AuthorArticleListCreateView(generics.ListCreateAPIView):
    """Yazarin makaleleri: listeleme + olusturma."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AuthorArticleCreateSerializer
        return AuthorArticleListSerializer

    def get_queryset(self):
        qs = Article.objects.filter(
            author=self.request.user,
        ).select_related('category').order_by('-updated_at')

        # Filtreleme
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title_tr__icontains=search) | Q(title_en__icontains=search)
            )

        return qs


class AuthorArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Makale detay, duzenleme, silme."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return AuthorArticleDetailSerializer
        return AuthorArticleDetailSerializer

    def get_queryset(self):
        return Article.objects.filter(
            author=self.request.user,
        ).select_related('category')

    def perform_destroy(self, instance):
        if instance.status != 'draft':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Sadece taslak makaleler silinebilir.')
        instance.delete()


class AuthorArticleTransitionView(views.APIView):
    """
    Makale durum gecisi.

    Gecerli gecisler:
      draft → submit_for_review (review pipeline tetiklenir)
      published → archive
      archived → revert_to_draft
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    # Article.Status sadece draft/published/archived
    TRANSITIONS = {
        'draft': {
            'submit_for_review': 'published',  # Basit akis: draft -> published
        },
        'published': {
            'archive': 'archived',
        },
        'archived': {
            'revert_to_draft': 'draft',
        },
    }

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk, author=request.user)
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Makale bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ArticleStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        feedback = serializer.validated_data.get('feedback', '')

        current = article.status
        allowed = self.TRANSITIONS.get(current, {})

        if action not in allowed:
            return Response(
                {
                    'detail': f"'{current}' durumundaki bir makale icin '{action}' gecersiz.",
                    'allowed_actions': list(allowed.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = allowed[action]

        # submit_for_review icin pipeline calistir
        if action == 'submit_for_review':
            pipeline_result = self._run_review_pipeline(article, request.user)
            if pipeline_result and not pipeline_result.get('quality_passed', True):
                # Kalite kontrolunden gecemedi — draft olarak kalir
                return Response({
                    'detail': 'Makale kalite kontrolunden gecemedigi icin taslak olarak kaldi.',
                    'pipeline_result': pipeline_result,
                    'status': article.status,
                })

        # Durum guncelle
        article.status = new_status
        if new_status == 'published' and not article.published_at:
            article.published_at = timezone.now()
        article.save()

        # Yazar istatistiklerini guncelle
        if new_status == 'published':
            self._update_author_stats(request.user)

        logger.info(
            f"Article {article.id}: {current} -> {new_status} "
            f"(action={action}, user={request.user.email})"
        )

        # Bildirim gonder
        notify_article_transition(article, current, new_status, changed_by=request.user, feedback=feedback)

        return Response({
            'detail': f'Makale durumu guncellendi: {new_status}',
            'status': new_status,
            'article_id': str(article.id),
        })

    def _run_review_pipeline(self, article, user):
        """Makaleyi review pipeline'indan gecir."""
        try:
            from services.base_agent import BaseAgent
            from services.orchestrator import orchestrator
            import services.agents  # noqa: F401

            original_is_enabled = BaseAgent.is_enabled
            BaseAgent.is_enabled = lambda self: True

            try:
                result = orchestrator.run_chain(
                    'doctor_article_review',
                    input_data={
                        'title_tr': article.title_tr,
                        'body_tr': article.body_tr,
                        'excerpt_tr': article.excerpt_tr,
                        'article_id': str(article.id),
                    },
                    triggered_by=user,
                )

                # Review kaydini olustur
                overall_score = result.final_data.get('overall_score', 0)
                if isinstance(overall_score, str):
                    try:
                        overall_score = int(overall_score)
                    except (ValueError, TypeError):
                        overall_score = 0

                ArticleReview.objects.create(
                    article=article,
                    review_type='agent',
                    medical_accuracy_score=result.final_data.get('medical_accuracy_score', 0),
                    language_quality_score=result.final_data.get('language_quality_score', 0),
                    seo_score=result.final_data.get('seo_score', 0),
                    style_compliance_score=result.final_data.get('style_compliance_score', 0),
                    ethics_score=result.final_data.get('ethics_score', 0),
                    overall_score=overall_score,
                    decision='publish' if overall_score >= 60 else 'revise',
                    feedback=result.final_data.get('feedback', ''),
                    detailed_analysis=result.final_data,
                )

                # SEO alanlarini guncelle (pipeline'dan gelen)
                seo_fields_updated = False
                for field in ['seo_title_tr', 'seo_title_en', 'seo_description_tr', 'seo_description_en']:
                    val = result.final_data.get(field)
                    if val and not getattr(article, field):
                        setattr(article, field, val)
                        seo_fields_updated = True
                if seo_fields_updated:
                    article.save()

                return {
                    'success': result.success,
                    'overall_score': overall_score,
                    'quality_passed': overall_score >= 60,
                    'steps_completed': result.steps_completed,
                    'feedback': result.final_data.get('feedback', ''),
                }
            finally:
                BaseAgent.is_enabled = original_is_enabled

        except Exception as e:
            logger.error(f"Review pipeline hatasi: {e}")
            return None

    def _update_author_stats(self, user):
        """Yazarin makale sayisini guncelle."""
        try:
            author = user.doctor_profile.author_profile
            author.total_articles = (
                Article.objects.filter(author=user, status='published').count()
                + NewsArticle.objects.filter(author=author, status='published').count()
            )
            author.save(update_fields=['total_articles'])
            author.update_level()
        except Exception as e:
            logger.warning(f"Yazar istatistik guncelleme hatasi: {e}")


class AuthorArticleRunPipelineView(views.APIView):
    """
    Mevcut makale icin pipeline calistir.
    Ornegin: SEO optimize, kalite kontrol vb.
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    ALLOWED_PIPELINES = [
        'seo_optimize', 'legal_audit', 'quality_check', 'doctor_article_review',
    ]

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk, author=request.user)
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Makale bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        pipeline_name = request.data.get('pipeline', 'doctor_article_review')
        if pipeline_name not in self.ALLOWED_PIPELINES:
            return Response(
                {
                    'detail': f"Gecersiz pipeline: {pipeline_name}",
                    'allowed': self.ALLOWED_PIPELINES,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from services.base_agent import BaseAgent
            from services.orchestrator import orchestrator
            import services.agents  # noqa: F401

            original_is_enabled = BaseAgent.is_enabled
            BaseAgent.is_enabled = lambda self: True

            try:
                result = orchestrator.run_chain(
                    pipeline_name,
                    input_data={
                        'title_tr': article.title_tr,
                        'body_tr': article.body_tr,
                        'excerpt_tr': article.excerpt_tr,
                        'seo_title_tr': article.seo_title_tr,
                        'seo_description_tr': article.seo_description_tr,
                        'article_id': str(article.id),
                    },
                    triggered_by=request.user,
                )

                return Response({
                    'success': result.success,
                    'pipeline': pipeline_name,
                    'steps_completed': result.steps_completed,
                    'steps_failed': result.steps_failed,
                    'duration_ms': result.total_duration_ms,
                    'data': {
                        k: v for k, v in result.final_data.items()
                        if not k.startswith('__')
                    },
                })
            finally:
                BaseAgent.is_enabled = original_is_enabled

        except Exception as e:
            logger.error(f"Pipeline hatasi: {e}")
            return Response(
                {'detail': f'Pipeline hatasi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ═══════════════════════════════════════════════
# 3. HABER (NewsArticle) YÖNETİMİ
# ═══════════════════════════════════════════════

class AuthorNewsListCreateView(generics.ListCreateAPIView):
    """Yazarin haberleri: listeleme + olusturma."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AuthorNewsCreateSerializer
        return AuthorNewsListSerializer

    def get_queryset(self):
        author = _get_author_or_none(self.request.user)
        if not author:
            return NewsArticle.objects.none()

        qs = NewsArticle.objects.filter(
            author=author,
        ).order_by('-updated_at')

        # Filtreleme
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        category_filter = self.request.query_params.get('category')
        if category_filter:
            qs = qs.filter(category=category_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title_tr__icontains=search)

        return qs


class AuthorNewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Haber detay, duzenleme, silme."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_serializer_class(self):
        return AuthorNewsDetailSerializer

    def get_queryset(self):
        author = _get_author_or_none(self.request.user)
        if not author:
            return NewsArticle.objects.none()
        return NewsArticle.objects.filter(author=author)

    def perform_destroy(self, instance):
        if instance.status not in ('draft', 'revision'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Sadece taslak veya duzeltme bekleyen haberler silinebilir.')
        instance.delete()


class AuthorNewsTransitionView(views.APIView):
    """
    Haber durum gecisi.

    Gecerli gecisler (yazar icin):
      draft     → submit_for_review  → review
      revision  → submit_for_review  → review

    Admin/editor icin (sonra eklenecek):
      review   → approve  → approved
      review   → reject   → revision
      approved → publish  → published

    Yazar auto-publish hakki varsa:
      draft    → submit_for_review → published (direkt)
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    AUTHOR_TRANSITIONS = {
        'draft': {'submit_for_review': 'review'},
        'revision': {'submit_for_review': 'review'},
    }

    # Kıdemli yazar (level >= 2) direkt yayinlayabilir
    AUTOPUBLISH_TRANSITIONS = {
        'draft': {'submit_for_review': 'published'},
        'revision': {'submit_for_review': 'published'},
    }

    def post(self, request, pk):
        author = _get_author_or_none(request.user)
        if not author:
            return Response(
                {'detail': 'Yazar profiliniz bulunmuyor.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            news = NewsArticle.objects.get(pk=pk, author=author)
        except NewsArticle.DoesNotExist:
            return Response(
                {'detail': 'Haber bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NewsStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        feedback = serializer.validated_data.get('feedback', '')

        current = news.status

        # Auto-publish hakki var mi?
        if author.can_auto_publish:
            transitions = self.AUTOPUBLISH_TRANSITIONS
        else:
            transitions = self.AUTHOR_TRANSITIONS

        allowed = transitions.get(current, {})

        if action not in allowed:
            return Response(
                {
                    'detail': f"'{current}' durumundaki bir haber icin '{action}' gecersiz.",
                    'allowed_actions': list(allowed.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = allowed[action]

        news.status = new_status
        if new_status == 'published' and not news.published_at:
            news.published_at = timezone.now()
        news.save()

        # Yazar istatistiklerini guncelle
        if new_status == 'published':
            try:
                author.total_articles = (
                    Article.objects.filter(author=request.user, status='published').count()
                    + NewsArticle.objects.filter(author=author, status='published').count()
                )
                author.save(update_fields=['total_articles'])
                author.update_level()
            except Exception:
                pass

        logger.info(
            f"NewsArticle {news.id}: {current} -> {new_status} "
            f"(action={action}, user={request.user.email})"
        )

        # Bildirim gonder
        auto_pub = author.can_auto_publish and new_status == 'published'
        notify_news_transition(news, current, new_status, changed_by=request.user, feedback=feedback, auto_published=auto_pub)

        return Response({
            'detail': f'Haber durumu guncellendi: {new_status}',
            'status': new_status,
            'news_id': str(news.id),
            'auto_published': author.can_auto_publish and new_status == 'published',
        })


# ═══════════════════════════════════════════════
# 4. YAZAR İSTATİSTİKLERİ
# ═══════════════════════════════════════════════

class AuthorStatsView(views.APIView):
    """Yazar dashboard istatistikleri."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        author = _get_author_or_none(request.user)
        if not author:
            return Response(
                {'detail': 'Yazar profiliniz bulunmuyor.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Article istatistikleri
        article_stats = Article.objects.filter(
            author=request.user,
        ).values('status').annotate(count=Count('id'))
        article_by_status = {s['status']: s['count'] for s in article_stats}

        # NewsArticle istatistikleri
        news_stats = NewsArticle.objects.filter(
            author=author,
        ).values('status').annotate(count=Count('id'))
        news_by_status = {s['status']: s['count'] for s in news_stats}

        # Toplam goruntulenme
        total_news_views = NewsArticle.objects.filter(
            author=author,
        ).aggregate(total=Sum('view_count'))['total'] or 0

        # Son degerlendirmeler
        recent_reviews = ArticleReview.objects.filter(
            Q(article__author=request.user) | Q(news_article__author=author)
        ).order_by('-created_at')[:5]

        return Response({
            'author': {
                'name': author.doctor.user.get_full_name(),
                'level': author.author_level,
                'level_display': author.get_author_level_display(),
                'total_articles': author.total_articles,
                'total_views': author.total_views + total_news_views,
                'average_rating': float(author.average_rating),
                'can_auto_publish': author.can_auto_publish,
                'is_verified': author.is_verified,
            },
            'articles': {
                'total': sum(article_by_status.values()),
                'by_status': article_by_status,
            },
            'news': {
                'total': sum(news_by_status.values()),
                'by_status': news_by_status,
            },
            'recent_reviews': ArticleReviewSerializer(recent_reviews, many=True).data,
        })
