from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('initiate/', views.InitiatePaymentView.as_view(), name='payment-initiate'),
    path('callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
]
