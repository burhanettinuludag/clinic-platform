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
from .views_devops import DevOpsGenerateView, DevOpsReviewView
from .views_analytics import AnalyticsOverviewView, ContentStatsView
from .views_marketing import (
    MarketingCampaignListCreateView,
    MarketingCampaignDetailView,
    MarketingCampaignApproveView,
    MarketingCampaignRegenerateView,
)
from .views_broken_links import (
    BrokenLinkListView,
    BrokenLinkStatsView,
    BrokenLinkScanListView,
    TriggerScanView,
    FixBrokenLinkView,
    BulkBrokenLinkActionView,
    RecheckBrokenLinkView,
)
from .views_agents import (
    AgentListView,
    TriggerAgentView,
    AgentTriggerHistoryView,
    AgentStatsView,
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

    # Analytics
    path('analytics/overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('analytics/content-stats/', ContentStatsView.as_view(), name='analytics-content-stats'),

    # DevOps Agent
    path('devops/generate/', DevOpsGenerateView.as_view(), name='devops-generate'),
    path('devops/review/', DevOpsReviewView.as_view(), name='devops-review'),

    # Toplu islemler
    path('editor/articles/bulk-transition/', EditorBulkArticleTransitionView.as_view(), name='editor-bulk-article-transition'),
    path('editor/news/bulk-transition/', EditorBulkNewsTransitionView.as_view(), name='editor-bulk-news-transition'),

    # ═══ Agent Management ═══
    path('agents/', AgentListView.as_view(), name='agent-list'),
    path('agents/trigger/', TriggerAgentView.as_view(), name='agent-trigger'),
    path('agents/history/', AgentTriggerHistoryView.as_view(), name='agent-trigger-history'),
    path('agents/stats/', AgentStatsView.as_view(), name='agent-stats'),

    # ═══ Broken Links ═══
    path('broken-links/', BrokenLinkListView.as_view(), name='broken-links'),
    path('broken-links/stats/', BrokenLinkStatsView.as_view(), name='broken-links-stats'),
    path('broken-links/scans/', BrokenLinkScanListView.as_view(), name='broken-link-scans'),
    path('broken-links/scan/', TriggerScanView.as_view(), name='trigger-scan'),
    path('broken-links/<uuid:pk>/fix/', FixBrokenLinkView.as_view(), name='fix-broken-link'),
    path('broken-links/<uuid:pk>/recheck/', RecheckBrokenLinkView.as_view(), name='recheck-broken-link'),
    path('broken-links/bulk/', BulkBrokenLinkActionView.as_view(), name='bulk-broken-link-action'),

    # ═══ Marketing Campaign ═══
    path('marketing/', MarketingCampaignListCreateView.as_view(), name='marketing-campaigns'),
    path('marketing/<uuid:pk>/', MarketingCampaignDetailView.as_view(), name='marketing-campaign-detail'),
    path('marketing/<uuid:pk>/approve/', MarketingCampaignApproveView.as_view(), name='marketing-campaign-approve'),
    path('marketing/<uuid:pk>/regenerate/', MarketingCampaignRegenerateView.as_view(), name='marketing-campaign-regenerate'),
]
