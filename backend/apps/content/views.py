from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsPatient
from .models import ContentCategory, Article, EducationItem, EducationProgress
from .serializers import (
    ContentCategorySerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
    EducationItemSerializer,
    EducationProgressSerializer,
)


class ContentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentCategory.objects.filter(parent__isnull=True)
    serializer_class = ContentCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
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

    def get_queryset(self):
        qs = EducationItem.objects.filter(
            is_published=True
        ).select_related('disease_module', 'category')

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
        return Response(EducationProgressSerializer(progress).data)


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Public haber listesi ve detayi."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = NewsArticle.objects.filter(
            status='published'
        ).select_related('author__doctor__user').order_by('-published_at')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        priority = self.request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)
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
