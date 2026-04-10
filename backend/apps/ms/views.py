from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import MSCategory, MSArticle, MSTip, MSFAQ
from .serializers import (
    MSCategorySerializer,
    MSArticleListSerializer,
    MSArticleDetailSerializer,
    MSTipSerializer,
    MSFAQSerializer,
)


class MSCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """MS kategorileri - herkese açık."""
    queryset = MSCategory.objects.filter(is_active=True)
    serializer_class = MSCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class MSArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """MS makaleleri - herkese açık, ücretsiz."""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['article_type', 'category__slug', 'is_featured']
    search_fields = ['title_tr', 'title_en', 'content_tr', 'content_en']
    ordering_fields = ['created_at', 'view_count', 'order']
    ordering = ['order', '-created_at']

    def get_queryset(self):
        return MSArticle.objects.filter(
            is_published=True
        ).select_related('category')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MSArticleDetailSerializer
        return MSArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        MSArticle.objects.filter(pk=instance.pk).update(
            view_count=F('view_count') + 1
        )
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Öne çıkan makaleler."""
        qs = self.get_queryset().filter(is_featured=True)[:6]
        serializer = MSArticleListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class MSTipViewSet(viewsets.ReadOnlyModelViewSet):
    """MS önerileri - herkese açık."""
    queryset = MSTip.objects.filter(is_active=True)
    serializer_class = MSTipSerializer
    permission_classes = [permissions.AllowAny]


class MSFAQViewSet(viewsets.ReadOnlyModelViewSet):
    """MS SSS - herkese açık."""
    queryset = MSFAQ.objects.filter(is_active=True)
    serializer_class = MSFAQSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug']
