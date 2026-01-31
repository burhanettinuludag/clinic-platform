from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskTemplateViewSet, TaskCompletionViewSet

router = DefaultRouter()
router.register('templates', TaskTemplateViewSet, basename='task-template')
router.register('completions', TaskCompletionViewSet, basename='task-completion')

urlpatterns = [
    path('', include(router.urls)),
]
