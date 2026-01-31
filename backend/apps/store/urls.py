from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    LicenseViewSet,
)

router = DefaultRouter()
router.register('categories', ProductCategoryViewSet, basename='product-category')
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')
router.register('licenses', LicenseViewSet, basename='license')

urlpatterns = [
    path('', include(router.urls)),
]
