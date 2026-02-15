from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContentCategoryViewSet,
    ArticleViewSet,
    NewsArticleViewSet,
    EducationItemViewSet,
    EducationProgressViewSet,
)

router = DefaultRouter()
router.register('categories', ContentCategoryViewSet, basename='content-category')
router.register('articles', ArticleViewSet, basename='article')
router.register('news', NewsArticleViewSet, basename='news-article')
router.register('education', EducationItemViewSet, basename='education-item')
router.register('education-progress', EducationProgressViewSet, basename='education-progress')

urlpatterns = [
    path('', include(router.urls)),
]
