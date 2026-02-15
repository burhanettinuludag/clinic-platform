"""
Social Media API URL Configuration.

All endpoints under /api/v1/social/
"""

from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # === Accounts ===
    path('accounts/', views.SocialAccountListCreateView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', views.SocialAccountDetailView.as_view(), name='account-detail'),
    path('accounts/<uuid:pk>/validate/', views.SocialAccountValidateView.as_view(), name='account-validate'),
    path('accounts/<uuid:pk>/refresh-token/', views.SocialAccountRefreshTokenView.as_view(), name='account-refresh-token'),

    # === Campaigns ===
    path('campaigns/', views.SocialCampaignListCreateView.as_view(), name='campaign-list'),
    path('campaigns/<uuid:pk>/', views.SocialCampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<uuid:pk>/regenerate/', views.SocialCampaignRegenerateView.as_view(), name='campaign-regenerate'),
    path('campaigns/<uuid:pk>/approve-all/', views.SocialCampaignApproveAllView.as_view(), name='campaign-approve-all'),

    # === Posts ===
    path('posts/', views.SocialPostListCreateView.as_view(), name='post-list'),
    path('posts/<uuid:pk>/', views.SocialPostDetailView.as_view(), name='post-detail'),
    path('posts/<uuid:pk>/approve/', views.SocialPostApproveView.as_view(), name='post-approve'),
    path('posts/<uuid:pk>/schedule/', views.SocialPostScheduleView.as_view(), name='post-schedule'),
    path('posts/<uuid:pk>/publish-now/', views.SocialPostPublishNowView.as_view(), name='post-publish-now'),
    path('posts/<uuid:pk>/retry/', views.SocialPostRetryView.as_view(), name='post-retry'),

    # === Bulk Operations ===
    path('posts/bulk-action/', views.BulkPostActionView.as_view(), name='post-bulk-action'),

    # === Calendar ===
    path('calendar/', views.SocialCalendarView.as_view(), name='calendar'),

    # === Dashboard ===
    path('dashboard/', views.SocialDashboardStatsView.as_view(), name='dashboard'),

    # === Image Generation ===
    path('image-preview/', views.ImagePreviewView.as_view(), name='image-preview'),
    path('image-templates/', views.ImageTemplatesView.as_view(), name='image-templates'),
]
