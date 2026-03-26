from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import (
    SleepCategory, SleepArticle, SleepTip, SleepFAQ,
    SleepScreeningTest,
)
from .serializers import (
    SleepCategorySerializer,
    SleepArticleListSerializer,
    SleepArticleDetailSerializer,
    SleepTipSerializer,
    SleepFAQSerializer,
    SleepScreeningTestListSerializer,
    SleepScreeningTestDetailSerializer,
)


class SleepCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Uyku kategorileri - herkese acik."""
    queryset = SleepCategory.objects.filter(is_active=True)
    serializer_class = SleepCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class SleepArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Uyku makaleleri - herkese acik, ucretsiz."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['article_type', 'category__slug', 'related_disease', 'is_featured']
    search_fields = ['title_tr', 'title_en', 'content_tr', 'content_en']
    ordering_fields = ['created_at', 'view_count', 'order']
    ordering = ['order', '-created_at']

    def get_queryset(self):
        return SleepArticle.objects.filter(
            is_published=True
        ).select_related('category')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SleepArticleDetailSerializer
        return SleepArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Goruntulenme sayisini artir
        SleepArticle.objects.filter(pk=instance.pk).update(
            view_count=F('view_count') + 1
        )
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """One cikan makaleler."""
        qs = self.get_queryset().filter(is_featured=True)[:6]
        serializer = SleepArticleListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-disease/(?P<disease>[a-z]+)')
    def by_disease(self, request, disease=None):
        """Belirli bir hastaliga ait uyku makaleleri."""
        qs = self.get_queryset().filter(related_disease=disease)
        serializer = SleepArticleListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class SleepTipViewSet(viewsets.ReadOnlyModelViewSet):
    """Uyku onerileri - herkese acik."""
    queryset = SleepTip.objects.filter(is_active=True)
    serializer_class = SleepTipSerializer
    permission_classes = [permissions.AllowAny]


class SleepFAQViewSet(viewsets.ReadOnlyModelViewSet):
    """Uyku SSS - herkese acik."""
    queryset = SleepFAQ.objects.filter(is_active=True)
    serializer_class = SleepFAQSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug']


class SleepScreeningTestViewSet(viewsets.ReadOnlyModelViewSet):
    """Uyku farkındalık testleri - herkese açık, anonim."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return SleepScreeningTest.objects.filter(
            is_active=True
        ).prefetch_related(
            'questions__options',
            'result_ranges',
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SleepScreeningTestDetailSerializer
        return SleepScreeningTestListSerializer
