"""
Editor / Admin icerik onay ve yonetim endpoint'leri.

Bu view'lar admin ve editor rolundeki kullanicilar icindir.
Yazarlarin gonderdigi icerikleri inceleme, onaylama, reddetme ve yayinlama
islemlerini kapsar.

Endpoint'ler:
─────────────────────────────────────────────
İNCELEME KUYRUGU
  GET    /api/v1/doctor/editor/review-queue/           → Inceleme bekleyen icerikler
  GET    /api/v1/doctor/editor/review-queue/stats/     → Kuyruk istatistikleri

MAKALE (Article) ONAY
  GET    /api/v1/doctor/editor/articles/               → Tum makaleleri listele (filtrelenebilir)
  GET    /api/v1/doctor/editor/articles/<id>/          → Makale detay + review gecmisi
  POST   /api/v1/doctor/editor/articles/<id>/review/   → Degerlendirme yap (skor + karar)
  POST   /api/v1/doctor/editor/articles/<id>/transition/ → Durum gecisi (approve/reject/publish)

HABER (NewsArticle) ONAY
  GET    /api/v1/doctor/editor/news/                   → Tum haberleri listele
  GET    /api/v1/doctor/editor/news/<id>/              → Haber detay + review gecmisi
  POST   /api/v1/doctor/editor/news/<id>/review/       → Degerlendirme yap
  POST   /api/v1/doctor/editor/news/<id>/transition/   → Durum gecisi

YAZAR YÖNETİMİ
  GET    /api/v1/doctor/editor/authors/                → Yazar listesi
  POST   /api/v1/doctor/editor/authors/<id>/verify/    → Yazar dogrulama
"""

import logging

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.utils import timezone
from django.db.models import Q, Count

from apps.accounts.models import DoctorAuthor
from apps.content.models import Article, NewsArticle, ArticleReview
from .serializers_author import (
    DoctorAuthorListSerializer,
    AuthorArticleListSerializer,
    AuthorArticleDetailSerializer,
    AuthorNewsListSerializer,
    AuthorNewsDetailSerializer,
    ArticleReviewSerializer,
)
from apps.notifications.content_notifications import (
    notify_article_transition,
    notify_news_transition,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# PERMISSION
# ═══════════════════════════════════════════════

class IsEditorOrAdmin(BasePermission):
    """
    Editor veya admin rolundeki kullanicilar.
    Editor = DoctorAuthor.author_level >= 4
    Admin = CustomUser.role == 'admin'
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Admin rolu
        if request.user.role == 'admin' or request.user.is_staff:
            return True
        # Editor seviyesindeki doktor yazar
        try:
            author = request.user.doctor_profile.author_profile
            return author.author_level >= 4
        except Exception:
            return False


# ═══════════════════════════════════════════════
# REVIEW SERIALIZERS (bu dosyaya ozel)
# ═══════════════════════════════════════════════

from rest_framework import serializers


class EditorReviewCreateSerializer(serializers.Serializer):
    """Editor degerlendirmesi olusturma."""
    medical_accuracy_score = serializers.IntegerField(min_value=0, max_value=100, default=0)
    language_quality_score = serializers.IntegerField(min_value=0, max_value=100, default=0)
    seo_score = serializers.IntegerField(min_value=0, max_value=100, default=0)
    style_compliance_score = serializers.IntegerField(min_value=0, max_value=100, default=0)
    ethics_score = serializers.IntegerField(min_value=0, max_value=100, default=0)
    decision = serializers.ChoiceField(choices=['publish', 'revise', 'reject'])
    feedback = serializers.CharField(required=False, allow_blank=True, default='')
    internal_notes = serializers.CharField(required=False, allow_blank=True, default='')


class EditorTransitionSerializer(serializers.Serializer):
    """Editor durum gecisi."""
    action = serializers.ChoiceField(
        choices=['approve', 'reject', 'publish', 'archive', 'revert_to_draft'],
    )
    feedback = serializers.CharField(required=False, allow_blank=True, default='')


# ═══════════════════════════════════════════════
# 1. İNCELEME KUYRUGU
# ═══════════════════════════════════════════════

class ReviewQueueView(views.APIView):
    """Inceleme bekleyen tum icerikler (Article + NewsArticle)."""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        # Article: sadece draft + body dolu olanlar (submit edilmis sayilir)
        # Gercek projede ayri bir 'review' statusu eklenebilir Article'a da
        pending_articles = Article.objects.filter(
            status='draft',
        ).exclude(
            body_tr='',
        ).select_related('category', 'author').order_by('-updated_at')[:20]

        # NewsArticle: review durumundakiler
        pending_news = NewsArticle.objects.filter(
            status='review',
        ).select_related('author').order_by('-updated_at')[:20]

        articles_data = AuthorArticleListSerializer(pending_articles, many=True).data
        news_data = AuthorNewsListSerializer(pending_news, many=True).data

        return Response({
            'articles': articles_data,
            'news': news_data,
            'total_pending': len(articles_data) + len(news_data),
        })


class ReviewQueueStatsView(views.APIView):
    """Kuyruk istatistikleri."""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        article_stats = Article.objects.values('status').annotate(
            count=Count('id'),
        )
        news_stats = NewsArticle.objects.values('status').annotate(
            count=Count('id'),
        )

        # Son 7 gunde yapilan review sayisi
        week_ago = timezone.now() - timezone.timedelta(days=7)
        recent_reviews = ArticleReview.objects.filter(
            created_at__gte=week_ago,
        ).count()

        return Response({
            'articles_by_status': {s['status']: s['count'] for s in article_stats},
            'news_by_status': {s['status']: s['count'] for s in news_stats},
            'reviews_last_7_days': recent_reviews,
            'pending_news_review': NewsArticle.objects.filter(status='review').count(),
            'pending_news_approved': NewsArticle.objects.filter(status='approved').count(),
        })


# ═══════════════════════════════════════════════
# 2. MAKALE (Article) ONAY
# ═══════════════════════════════════════════════

class EditorArticleListView(generics.ListAPIView):
    """Tum makaleler — editor gorunumu."""
    serializer_class = AuthorArticleListSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get_queryset(self):
        qs = Article.objects.select_related('category', 'author').order_by('-updated_at')

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        author_filter = self.request.query_params.get('author_id')
        if author_filter:
            qs = qs.filter(author_id=author_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title_tr__icontains=search) | Q(title_en__icontains=search)
            )

        return qs


class EditorArticleDetailView(generics.RetrieveAPIView):
    """Makale detay + tum review gecmisi."""
    serializer_class = AuthorArticleDetailSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    queryset = Article.objects.select_related('category', 'author')


class EditorArticleReviewView(views.APIView):
    """Makaleye editor degerlendirmesi ekle."""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Makale bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EditorReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Overall score hesapla
        scores = [
            data['medical_accuracy_score'],
            data['language_quality_score'],
            data['seo_score'],
            data['style_compliance_score'],
            data['ethics_score'],
        ]
        non_zero = [s for s in scores if s > 0]
        overall = round(sum(non_zero) / len(non_zero)) if non_zero else 0

        # Review tipi belirle
        review_type = 'editor'
        if request.user.is_staff or request.user.role == 'admin':
            review_type = 'chief_editor'

        review = ArticleReview.objects.create(
            article=article,
            review_type=review_type,
            reviewer=request.user,
            medical_accuracy_score=data['medical_accuracy_score'],
            language_quality_score=data['language_quality_score'],
            seo_score=data['seo_score'],
            style_compliance_score=data['style_compliance_score'],
            ethics_score=data['ethics_score'],
            overall_score=overall,
            decision=data['decision'],
            feedback=data['feedback'],
            internal_notes=data['internal_notes'],
        )

        logger.info(
            f"Article {article.id} reviewed by {request.user.email}: "
            f"score={overall}, decision={data['decision']}"
        )

        return Response(
            ArticleReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class EditorArticleTransitionView(views.APIView):
    """
    Editor/admin makale durum gecisi.

    Gecerli gecisler:
      draft     → publish  (editor direkt yayinlayabilir)
      draft     → archive
      published → archive
      archived  → revert_to_draft
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    TRANSITIONS = {
        'draft': ['publish', 'archive'],
        'published': ['archive'],
        'archived': ['revert_to_draft'],
    }

    STATUS_MAP = {
        'publish': 'published',
        'archive': 'archived',
        'revert_to_draft': 'draft',
    }

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Makale bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EditorTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        feedback = serializer.validated_data.get('feedback', '')

        current = article.status
        allowed = self.TRANSITIONS.get(current, [])

        if action not in allowed:
            return Response(
                {
                    'detail': f"'{current}' durumundaki makale icin '{action}' gecersiz.",
                    'allowed_actions': allowed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = self.STATUS_MAP[action]
        article.status = new_status
        if new_status == 'published' and not article.published_at:
            article.published_at = timezone.now()
        article.save()

        # Yayinlandiginda yazar istatistiklerini guncelle
        if new_status == 'published' and article.author:
            self._update_author_stats(article.author)

        logger.info(
            f"[EDITOR] Article {article.id}: {current} -> {new_status} "
            f"by {request.user.email} (action={action})"
        )

        notify_article_transition(article, current, new_status, changed_by=request.user, feedback=feedback)

        return Response({
            'detail': f'Makale durumu guncellendi: {new_status}',
            'status': new_status,
            'article_id': str(article.id),
            'changed_by': request.user.email,
        })

    def _update_author_stats(self, user):
        try:
            author = user.doctor_profile.author_profile
            article_count = Article.objects.filter(
                Q(author=user) | Q(doctor_author=author), status='published'
            ).distinct().count()
            news_count = NewsArticle.objects.filter(author=author, status='published').count()
            author.total_articles = article_count + news_count
            author.save(update_fields=['total_articles'])
            author.update_level()
        except Exception:
            pass


# ═══════════════════════════════════════════════
# 3. HABER (NewsArticle) ONAY
# ═══════════════════════════════════════════════

class EditorNewsListView(generics.ListAPIView):
    """Tum haberler — editor gorunumu."""
    serializer_class = AuthorNewsListSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get_queryset(self):
        qs = NewsArticle.objects.select_related('author').order_by('-updated_at')

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


class EditorNewsDetailView(generics.RetrieveAPIView):
    """Haber detay + tum review gecmisi."""
    serializer_class = AuthorNewsDetailSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    queryset = NewsArticle.objects.select_related('author')


class EditorNewsReviewView(views.APIView):
    """Habere editor degerlendirmesi ekle."""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            news = NewsArticle.objects.get(pk=pk)
        except NewsArticle.DoesNotExist:
            return Response(
                {'detail': 'Haber bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EditorReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        scores = [
            data['medical_accuracy_score'],
            data['language_quality_score'],
            data['seo_score'],
            data['style_compliance_score'],
            data['ethics_score'],
        ]
        non_zero = [s for s in scores if s > 0]
        overall = round(sum(non_zero) / len(non_zero)) if non_zero else 0

        review_type = 'editor'
        if request.user.is_staff or request.user.role == 'admin':
            review_type = 'chief_editor'

        review = ArticleReview.objects.create(
            news_article=news,
            review_type=review_type,
            reviewer=request.user,
            medical_accuracy_score=data['medical_accuracy_score'],
            language_quality_score=data['language_quality_score'],
            seo_score=data['seo_score'],
            style_compliance_score=data['style_compliance_score'],
            ethics_score=data['ethics_score'],
            overall_score=overall,
            decision=data['decision'],
            feedback=data['feedback'],
            internal_notes=data['internal_notes'],
        )

        logger.info(
            f"NewsArticle {news.id} reviewed by {request.user.email}: "
            f"score={overall}, decision={data['decision']}"
        )

        return Response(
            ArticleReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class EditorNewsTransitionView(views.APIView):
    """
    Editor/admin haber durum gecisi.

    Tam akis:
      draft    → (yazar submit) → review
      review   → approve  → approved
      review   → reject   → revision
      approved → publish  → published
      published → archive → archived
      archived → revert_to_draft → draft
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    TRANSITIONS = {
        'review': ['approve', 'reject'],
        'approved': ['publish'],
        'published': ['archive'],
        'archived': ['revert_to_draft'],
        # Editor draft'tan da direkt yayinlayabilir
        'draft': ['approve', 'publish', 'archive'],
        'revision': ['approve', 'reject'],
    }

    STATUS_MAP = {
        'approve': 'approved',
        'reject': 'revision',
        'publish': 'published',
        'archive': 'archived',
        'revert_to_draft': 'draft',
    }

    def post(self, request, pk):
        try:
            news = NewsArticle.objects.get(pk=pk)
        except NewsArticle.DoesNotExist:
            return Response(
                {'detail': 'Haber bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EditorTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        feedback = serializer.validated_data.get('feedback', '')

        current = news.status
        allowed = self.TRANSITIONS.get(current, [])

        if action not in allowed:
            return Response(
                {
                    'detail': f"'{current}' durumundaki haber icin '{action}' gecersiz.",
                    'allowed_actions': allowed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = self.STATUS_MAP[action]

        # Reviewed_by kaydet
        if action in ('approve', 'reject'):
            news.reviewed_by = request.user

        news.status = new_status
        if new_status == 'published' and not news.published_at:
            news.published_at = timezone.now()
        news.save()

        # Yayinlandiginda yazar istatistiklerini guncelle
        if new_status == 'published' and news.author:
            self._update_news_author_stats(news.author)

        logger.info(
            f"[EDITOR] NewsArticle {news.id}: {current} -> {new_status} "
            f"by {request.user.email} (action={action})"
        )

        notify_news_transition(news, current, new_status, changed_by=request.user, feedback=feedback)

        return Response({
            'detail': f'Haber durumu guncellendi: {new_status}',
            'status': new_status,
            'news_id': str(news.id),
            'changed_by': request.user.email,
        })

    def _update_news_author_stats(self, author):
        try:
            author.total_articles = (
                Article.objects.filter(
                    author=author.doctor.user, status='published'
                ).count()
                + NewsArticle.objects.filter(
                    author=author, status='published'
                ).count()
            )
            author.save(update_fields=['total_articles'])
            author.update_level()
        except Exception:
            pass


# ═══════════════════════════════════════════════
# 4. YAZAR YÖNETİMİ
# ═══════════════════════════════════════════════

class EditorAuthorListView(generics.ListAPIView):
    """Tum yazarlar listesi."""
    serializer_class = DoctorAuthorListSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get_queryset(self):
        qs = DoctorAuthor.objects.select_related(
            'doctor__user',
        ).order_by('-author_level', '-total_articles')

        verified_filter = self.request.query_params.get('is_verified')
        if verified_filter is not None:
            qs = qs.filter(is_verified=verified_filter.lower() == 'true')

        specialty_filter = self.request.query_params.get('specialty')
        if specialty_filter:
            qs = qs.filter(primary_specialty=specialty_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(doctor__user__first_name__icontains=search)
                | Q(doctor__user__last_name__icontains=search)
                | Q(institution__icontains=search)
            )

        return qs


class EditorAuthorVerifyView(views.APIView):
    """Yazar dogrulama (is_verified = True)."""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            author = DoctorAuthor.objects.get(pk=pk)
        except DoctorAuthor.DoesNotExist:
            return Response(
                {'detail': 'Yazar bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        action = request.data.get('action', 'verify')  # verify / unverify

        if action == 'verify':
            author.is_verified = True
            author.verified_at = timezone.now()
            msg = 'Yazar dogrulandi.'
        elif action == 'unverify':
            author.is_verified = False
            author.verified_at = None
            msg = 'Yazar dogrulamasi kaldirildi.'
        else:
            return Response(
                {'detail': "Gecersiz aksiyon. 'verify' veya 'unverify' kullanin."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Level degisikligi
        new_level = request.data.get('author_level')
        if new_level is not None:
            try:
                new_level = int(new_level)
                if 0 <= new_level <= 4:
                    author.author_level = new_level
            except (ValueError, TypeError):
                pass

        author.save()

        logger.info(
            f"[EDITOR] Author {author.id} ({author.doctor.user.email}): "
            f"action={action}, verified={author.is_verified}, "
            f"level={author.author_level}, by={request.user.email}"
        )

        return Response({
            'detail': msg,
            'author_id': str(author.id),
            'is_verified': author.is_verified,
            'author_level': author.author_level,
        })



# ===============================================
# 5. TOPLU ISLEMLER (Bulk Operations)
# ===============================================

class EditorBulkArticleTransitionView(views.APIView):
    """Toplu makale durum gecisi. POST {"ids":["uuid1","uuid2"],"action":"publish","feedback":""}"""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    STATUS_MAP = {'approve': 'approved', 'reject': 'revision', 'publish': 'published', 'archive': 'archived', 'revert_to_draft': 'draft'}

    def post(self, request):
        ids = request.data.get('ids', [])
        action = request.data.get('action', '')
        feedback = request.data.get('feedback', '')
        if not ids or not action:
            return Response({'detail': 'ids ve action zorunlu.'}, status=status.HTTP_400_BAD_REQUEST)
        if action not in self.STATUS_MAP:
            return Response({'detail': f'Gecersiz action: {action}'}, status=status.HTTP_400_BAD_REQUEST)
        new_status = self.STATUS_MAP[action]
        articles = Article.objects.filter(id__in=ids)
        results = {'success': [], 'failed': []}
        for article in articles:
            old = article.status
            try:
                article.status = new_status
                if new_status == 'published' and not article.published_at:
                    article.published_at = timezone.now()
                article.save()
                from apps.notifications.content_notifications import notify_article_transition
                notify_article_transition(article, old, new_status, changed_by=request.user, feedback=feedback)
                results['success'].append({'id': str(article.id), 'title': article.title_tr, 'new_status': new_status})
            except Exception as e:
                results['failed'].append({'id': str(article.id), 'error': str(e)})
        logger.info(f"[EDITOR BULK] Articles: {len(results['success'])} ok, {len(results['failed'])} fail, action={action}")
        return Response({'detail': f"{len(results['success'])} makale guncellendi.", 'results': results})


class EditorBulkNewsTransitionView(views.APIView):
    """Toplu haber durum gecisi. POST {"ids":["uuid1","uuid2"],"action":"approve","feedback":""}"""
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    STATUS_MAP = {'approve': 'approved', 'reject': 'revision', 'publish': 'published', 'archive': 'archived', 'revert_to_draft': 'draft'}

    def post(self, request):
        ids = request.data.get('ids', [])
        action = request.data.get('action', '')
        feedback = request.data.get('feedback', '')
        if not ids or not action:
            return Response({'detail': 'ids ve action zorunlu.'}, status=status.HTTP_400_BAD_REQUEST)
        if action not in self.STATUS_MAP:
            return Response({'detail': f'Gecersiz action: {action}'}, status=status.HTTP_400_BAD_REQUEST)
        new_status = self.STATUS_MAP[action]
        news_list = NewsArticle.objects.filter(id__in=ids)
        results = {'success': [], 'failed': []}
        for news in news_list:
            old = news.status
            try:
                news.status = new_status
                if new_status == 'published' and not news.published_at:
                    news.published_at = timezone.now()
                news.save()
                from apps.notifications.content_notifications import notify_news_transition
                notify_news_transition(news, old, new_status, changed_by=request.user, feedback=feedback)
                results['success'].append({'id': str(news.id), 'title': news.title_tr, 'new_status': new_status})
            except Exception as e:
                results['failed'].append({'id': str(news.id), 'error': str(e)})
        logger.info(f"[EDITOR BULK] News: {len(results['success'])} ok, {len(results['failed'])} fail, action={action}")
        return Response({'detail': f"{len(results['success'])} haber guncellendi.", 'results': results})
