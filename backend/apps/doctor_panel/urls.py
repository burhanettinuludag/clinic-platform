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
from .views_editor import (
    ReviewQueueView,
    ReviewQueueStatsView,
    EditorArticleListView,
    EditorArticleDetailView,
    EditorArticleReviewView,
    EditorArticleTransitionView,
    EditorNewsListView,
    EditorNewsDetailView,
    EditorNewsReviewView,
    EditorNewsTransitionView,
    EditorAuthorListView,
    EditorAuthorVerifyView,
    EditorBulkArticleTransitionView,
    EditorBulkNewsTransitionView,
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

    # ═══ Editor / Admin Onay Islemleri ═══
    # Inceleme kuyrugu
    path('editor/review-queue/', ReviewQueueView.as_view(), name='editor-review-queue'),
    path('editor/review-queue/stats/', ReviewQueueStatsView.as_view(), name='editor-review-queue-stats'),

    # Makale onay
    path('editor/articles/', EditorArticleListView.as_view(), name='editor-articles'),
    path('editor/articles/<uuid:pk>/', EditorArticleDetailView.as_view(), name='editor-article-detail'),
    path('editor/articles/<uuid:pk>/review/', EditorArticleReviewView.as_view(), name='editor-article-review'),
    path('editor/articles/<uuid:pk>/transition/', EditorArticleTransitionView.as_view(), name='editor-article-transition'),

    # Haber onay
    path('editor/news/', EditorNewsListView.as_view(), name='editor-news'),
    path('editor/news/<uuid:pk>/', EditorNewsDetailView.as_view(), name='editor-news-detail'),
    path('editor/news/<uuid:pk>/review/', EditorNewsReviewView.as_view(), name='editor-news-review'),
    path('editor/news/<uuid:pk>/transition/', EditorNewsTransitionView.as_view(), name='editor-news-transition'),

    # Yazar yonetimi
    path('editor/authors/', EditorAuthorListView.as_view(), name='editor-authors'),
    path('editor/authors/<uuid:pk>/verify/', EditorAuthorVerifyView.as_view(), name='editor-author-verify'),

    # Toplu islemler
    path('editor/articles/bulk-transition/', EditorBulkArticleTransitionView.as_view(), name='editor-bulk-article-transition'),
    path('editor/news/bulk-transition/', EditorBulkNewsTransitionView.as_view(), name='editor-bulk-news-transition'),
]
