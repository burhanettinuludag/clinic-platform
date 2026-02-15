from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_site

# Admin routers
admin_router = DefaultRouter()
admin_router.register(r'config', views_site.AdminSiteConfigViewSet, basename='admin-config')
admin_router.register(r'feature-flags', views_site.AdminFeatureFlagViewSet, basename='admin-feature-flags')
admin_router.register(r'announcements', views_site.AdminAnnouncementViewSet, basename='admin-announcements')
admin_router.register(r'hero', views_site.AdminHomepageHeroViewSet, basename='admin-hero')
admin_router.register(r'social-links', views_site.AdminSocialLinkViewSet, basename='admin-social-links')

urlpatterns = [
    # Public endpoints
    path('config/public/', views_site.PublicSiteConfigView.as_view(), name='site-config-public'),
    path('announcements/active/', views_site.ActiveAnnouncementsView.as_view(), name='announcements-active'),
    path('hero/active/', views_site.ActiveHeroView.as_view(), name='hero-active'),
    path('social-links/', views_site.PublicSocialLinksView.as_view(), name='social-links-public'),
    path('feature-flags/', views_site.PublicFeatureFlagsView.as_view(), name='feature-flags-public'),

    # Admin endpoints
    path('admin/', include(admin_router.urls)),
    path('admin/dashboard-stats/', views_site.dashboard_stats_view, name='dashboard-stats'),
]
