from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.SleepCategoryViewSet, basename='sleep-category')
router.register('articles', views.SleepArticleViewSet, basename='sleep-article')
router.register('tips', views.SleepTipViewSet, basename='sleep-tip')
router.register('faqs', views.SleepFAQViewSet, basename='sleep-faq')
router.register('tests', views.SleepScreeningTestViewSet, basename='sleep-test')

urlpatterns = [
    path('', include(router.urls)),
]
