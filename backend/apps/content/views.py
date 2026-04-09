from django.db import models
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from apps.accounts.models import DoctorAuthor
from .models import (
    ContentCategory, Article, NewsArticle, EducationItem, EducationProgress,
    EducationQuiz, QuizAttempt,
)
from .serializers import (
    ContentCategorySerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
    EducationItemSerializer,
    EducationProgressSerializer,
    EducationQuizSerializer,
    EducationQuizListSerializer,
    QuizAttemptSerializer,
    NewsArticleListSerializer,
    NewsArticleDetailSerializer,
    PublicDoctorAuthorSerializer,
)


class ContentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentCategory.objects.filter(parent__isnull=True)
    serializer_class = ContentCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_featured']

    def get_queryset(self):
        return Article.objects.filter(
            status='published'
        ).select_related('category', 'author')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:5]
        serializer = ArticleListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class EducationItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EducationItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'category']
    pagination_class = None  # Tum egitim kartlarini tek seferde don

    def get_queryset(self):
        qs = EducationItem.objects.filter(
            is_published=True
        ).select_related('disease_module', 'category').order_by('category__slug', 'order')

        # Filter by disease_module slug
        disease_module = self.request.query_params.get('disease_module')
        if disease_module:
            qs = qs.filter(disease_module__slug=disease_module)

        return qs


class EducationProgressViewSet(viewsets.ModelViewSet):
    serializer_class = EducationProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return EducationProgress.objects.filter(
            patient=self.request.user
        ).select_related('education_item')

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        progress = self.get_object()
        progress.progress_percent = 100
        progress.completed_at = timezone.now()
        progress.save()

        # Gamification: puan + streak
        try:
            from apps.gamification.models import UserPoints, UserStreak
            points_obj, _ = UserPoints.objects.get_or_create(user=request.user)
            points_obj.add_points(5, f'Egitim tamamlandi: {progress.education_item.title_tr[:50]}')
            streak, _ = UserStreak.objects.get_or_create(
                user=request.user, streak_type='education',
            )
            streak.update_streak(timezone.now().date())
        except Exception:
            pass  # Gamification hatasi egitimi engellemez

        return Response(EducationProgressSerializer(progress).data)


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Public haber listesi ve detayi."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = NewsArticle.objects.filter(
            status='published'
        ).select_related('author__doctor__user').prefetch_related('related_diseases').order_by('-published_at')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        priority = self.request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)
        disease = self.request.query_params.get('disease')
        if disease:
            qs = qs.filter(related_diseases__slug=disease)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # View count artir
        NewsArticle.objects.filter(pk=instance.pk).update(view_count=models.F('view_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PublicDoctorAuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """Public doktor profilleri - SEO friendly."""
    serializer_class = PublicDoctorAuthorSerializer
    permission_classes = [AllowAny]
    queryset = DoctorAuthor.objects.filter(is_active=True, is_verified=True).select_related('doctor__user')

    def get_object(self):
        pk = self.kwargs['pk']
        # slug-uuid8 formatinda gelebilir
        if '-' in str(pk) and len(str(pk)) > 8:
            uuid_part = str(pk).split('-')[-1]
            return self.get_queryset().filter(id__startswith=uuid_part).first() or super().get_object()
        return super().get_object()


class PublicEducationViewSet(viewsets.ReadOnlyModelViewSet):
    """Public egitim icerikleri - SSR friendly."""
    serializer_class = EducationItemSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'category']

    def get_queryset(self):
        return EducationItem.objects.filter(
            is_published=True
        ).select_related('disease_module', 'category')


class PublicNewsViewSet(viewsets.ReadOnlyModelViewSet):
    """Public haberler - SSR friendly."""
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = 'slug'

    def get_queryset(self):
        from apps.content.models import NewsArticle
        qs = NewsArticle.objects.filter(
            status='published'
        ).select_related('author__doctor__user').prefetch_related('related_diseases').order_by('-published_at', '-created_at')
        disease = self.request.query_params.get('disease')
        if disease:
            qs = qs.filter(related_diseases__slug=disease)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        # featured: ilk N taneyi one cikar (okunma sayisina gore)
        featured = self.request.query_params.get('featured')
        if featured:
            try:
                n = int(featured)
                return qs.order_by('-view_count', '-published_at')[:n]
            except (ValueError, TypeError):
                pass
        return qs

    def get_serializer_class(self):
        from apps.content.serializers import NewsArticleListSerializer, NewsArticleDetailSerializer
        if self.action == 'retrieve':
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # View count artir
        NewsArticle.objects.filter(pk=instance.pk).update(view_count=models.F('view_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# Education Quiz Views
# ─────────────────────────────────────────────

class EducationQuizViewSet(viewsets.ReadOnlyModelViewSet):
    """Egitim quizleri - modul sonunda bilgi testi."""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    pagination_class = None  # Tum quizleri tek seferde don

    def get_queryset(self):
        qs = EducationQuiz.objects.filter(
            is_published=True
        ).prefetch_related('questions').select_related('disease_module', 'category')

        disease_module = self.request.query_params.get('disease_module')
        if disease_module:
            qs = qs.filter(disease_module__slug=disease_module)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EducationQuizSerializer
        return EducationQuizListSerializer


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """Hasta quiz denemeleri."""
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return QuizAttempt.objects.filter(
            patient=self.request.user
        ).select_related('quiz')

    def perform_create(self, serializer):
        quiz = serializer.validated_data['quiz']
        answers = serializer.validated_data.get('answers', [])

        # Skor hesapla: soru seceneklerinden dogru cevabi bul
        questions_map = {str(q.id): q for q in quiz.questions.all()}
        correct_count = 0
        evaluated_answers = []

        for answer in answers:
            q_id = str(answer.get('question_id', ''))
            selected_idx = answer.get('selected_option_index', -1)
            question = questions_map.get(q_id)
            is_correct = False

            if question and question.options and 0 <= selected_idx < len(question.options):
                is_correct = question.options[selected_idx].get('is_correct', False)

            if is_correct:
                correct_count += 1

            evaluated_answers.append({
                'question_id': q_id,
                'selected_option_index': selected_idx,
                'is_correct': is_correct,
            })

        total = quiz.questions.count()
        pass_threshold = quiz.passing_score_percent
        passed = (correct_count / total * 100) >= pass_threshold if total > 0 else False

        attempt = serializer.save(
            patient=self.request.user,
            score=correct_count,
            total_questions=total,
            passed=passed,
            answers=evaluated_answers,
            completed_at=timezone.now(),
        )

        # Gamification: puan + streak
        if passed:
            try:
                from apps.gamification.models import UserPoints, UserStreak
                points_obj, _ = UserPoints.objects.get_or_create(user=self.request.user)
                reward = quiz.points_reward
                # Tam puan bonusu
                if correct_count == total:
                    reward += 5
                points_obj.add_points(reward, f'Quiz gecildi: {quiz.title_tr[:50]}')

                streak, _ = UserStreak.objects.get_or_create(
                    user=self.request.user, streak_type='education',
                )
                streak.update_streak(timezone.now().date())
            except Exception:
                pass
