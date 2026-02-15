from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_upload import ImageUploadView
from .views import PublicDoctorAuthorViewSet, PublicNewsViewSet, PublicEducationViewSet,\
     (
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
router.register('public-news', PublicNewsViewSet, basename='public-news')
router.register('public-education', PublicEducationViewSet, basename='public-education')
router.register('doctors', PublicDoctorAuthorViewSet, basename='public-doctor')
router.register('education-progress', EducationProgressViewSet, basename='education-progress')

urlpatterns = [
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
    path('', include(router.urls)),
]
