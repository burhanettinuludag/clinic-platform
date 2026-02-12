from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiseaseModuleViewSet, PatientModuleViewSet

module_router = DefaultRouter()
module_router.register('', DiseaseModuleViewSet, basename='disease-module')

enrollment_router = DefaultRouter()
enrollment_router.register('', PatientModuleViewSet, basename='patient-module')

urlpatterns = [
    path('enrollments/', include(enrollment_router.urls)),
    path('', include(module_router.urls)),
]
