from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import ProductCategory, Product, Order, OrderItem, License
from .serializers import (
    ProductCategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    LicenseSerializer,
)


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'product_type', 'is_featured']

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related('category')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ProductListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items')

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']
        total = 0
        order_items = []

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            license_type = item_data['license_type']
            quantity = item_data.get('quantity', 1)

            price_field = f'price_{license_type}'
            unit_price = getattr(product, price_field) or product.price_one_time or 0
            total += unit_price * quantity

            order_items.append({
                'product': product,
                'product_name': product.name_tr,
                'quantity': quantity,
                'unit_price': unit_price,
                'license_type': license_type,
            })

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            billing_name=serializer.validated_data['billing_name'],
            billing_address=serializer.validated_data['billing_address'],
            billing_city=serializer.validated_data['billing_city'],
            billing_zip_code=serializer.validated_data.get('billing_zip_code', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        for item in order_items:
            OrderItem.objects.create(order=order, **item)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LicenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return License.objects.filter(
            user=self.request.user
        ).select_related('product')

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        license_obj = self.get_object()
        if license_obj.current_activations >= license_obj.max_activations:
            return Response(
                {'error': 'Maximum activations reached.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if license_obj.expires_at and license_obj.expires_at < timezone.now():
            return Response(
                {'error': 'License has expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        license_obj.current_activations += 1
        license_obj.save()
        return Response(LicenseSerializer(license_obj, context={'request': request}).data)
