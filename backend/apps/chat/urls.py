from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatSessionViewSet,
    ConversationViewSet,
    DoctorConversationViewSet,
    DoctorListView,
    DoctorConversationStatsView,
)

router = DefaultRouter()
router.register('sessions', ChatSessionViewSet, basename='chat-session')
router.register('conversations', ConversationViewSet, basename='conversation')

doctor_router = DefaultRouter()
doctor_router.register('conversations', DoctorConversationViewSet, basename='doctor-conversation')

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='chat-doctors'),
    path('doctor/stats/', DoctorConversationStatsView.as_view(), name='doctor-chat-stats'),
    path('doctor/', include(doctor_router.urls)),
    path('', include(router.urls)),
]
