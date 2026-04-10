from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.MSCategoryViewSet, basename='ms-category')
router.register('articles', views.MSArticleViewSet, basename='ms-article')
router.register('tips', views.MSTipViewSet, basename='ms-tip')
router.register('faqs', views.MSFAQViewSet, basename='ms-faq')

urlpatterns = [
    path('', include(router.urls)),
]
