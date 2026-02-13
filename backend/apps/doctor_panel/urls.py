from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_content import GenerateContentView, GeneratedContentListView

router = DefaultRouter()
router.register(r'patients', views.DoctorPatientViewSet, basename='doctor-patients')

urlpatterns = [
    path('', include(router.urls)),
    path('alerts/', views.AlertListView.as_view(), name='doctor-alerts'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='doctor-dashboard-stats'),
    path('patients/<uuid:patient_id>/dementia-report/', views.DementiaReportView.as_view(), name='dementia-report'),
    # Icerik uretim
    path('generate-content/', GenerateContentView.as_view(), name='generate-content'),
    path('generated-content/', GeneratedContentListView.as_view(), name='generated-content-list'),
]
