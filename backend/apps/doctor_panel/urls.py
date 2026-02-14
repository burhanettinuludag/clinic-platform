from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_content import GenerateContentView, GeneratedContentListView
from .views_author import (
    AuthorProfileView,
    AuthorArticleListCreateView,
    AuthorArticleDetailView,
    AuthorArticleTransitionView,
    AuthorArticleRunPipelineView,
    AuthorNewsListCreateView,
    AuthorNewsDetailView,
    AuthorNewsTransitionView,
    AuthorStatsView,
)

router = DefaultRouter()
router.register(r'patients', views.DoctorPatientViewSet, basename='doctor-patients')

urlpatterns = [
    path('', include(router.urls)),
    path('alerts/', views.AlertListView.as_view(), name='doctor-alerts'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='doctor-dashboard-stats'),
    path('patients/<uuid:patient_id>/dementia-report/', views.DementiaReportView.as_view(), name='dementia-report'),

    # Icerik uretim (AI pipeline)
    path('generate-content/', GenerateContentView.as_view(), name='generate-content'),
    path('generated-content/', GeneratedContentListView.as_view(), name='generated-content-list'),

    # ═══ Yazar (Author) Islemleri ═══
    # Profil
    path('author/profile/', AuthorProfileView.as_view(), name='author-profile'),

    # Makale (Article) CRUD + workflow
    path('author/articles/', AuthorArticleListCreateView.as_view(), name='author-articles'),
    path('author/articles/<uuid:pk>/', AuthorArticleDetailView.as_view(), name='author-article-detail'),
    path('author/articles/<uuid:pk>/transition/', AuthorArticleTransitionView.as_view(), name='author-article-transition'),
    path('author/articles/<uuid:pk>/run-pipeline/', AuthorArticleRunPipelineView.as_view(), name='author-article-pipeline'),

    # Haber (NewsArticle) CRUD + workflow
    path('author/news/', AuthorNewsListCreateView.as_view(), name='author-news'),
    path('author/news/<uuid:pk>/', AuthorNewsDetailView.as_view(), name='author-news-detail'),
    path('author/news/<uuid:pk>/transition/', AuthorNewsTransitionView.as_view(), name='author-news-transition'),

    # Yazar istatistikleri
    path('author/stats/', AuthorStatsView.as_view(), name='author-stats'),
]
