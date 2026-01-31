from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiseaseModuleViewSet, PatientModuleViewSet

router = DefaultRouter()
router.register('', DiseaseModuleViewSet, basename='disease-module')
router.register('enrollments', PatientModuleViewSet, basename='patient-module')

urlpatterns = [
    path('', include(router.urls)),
]
