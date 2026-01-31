from rest_framework import serializers
from .models import ProductCategory, Product, Order, OrderItem, License


class ProductCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'slug', 'name', 'name_tr', 'name_en', 'description', 'order']

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)


class ProductListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'short_description', 'product_type',
            'category', 'category_name', 'featured_image',
            'price_monthly', 'price_yearly', 'price_one_time',
            'currency', 'is_featured', 'version',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_short_description(self, obj):
        return getattr(obj, f'short_description_{self._get_lang()}', obj.short_description_tr)

    def get_category_name(self, obj):
        if obj.category:
            return getattr(obj.category, f'name_{self._get_lang()}', obj.category.name_tr)
        return None


class ProductDetailSerializer(ProductListSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'description', 'short_description',
            'product_type', 'category', 'category_name', 'featured_image',
            'screenshots', 'price_monthly', 'price_yearly', 'price_one_time',
            'currency', 'is_featured', 'version', 'system_requirements',
        ]

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'license_type']
        read_only_fields = ['product_name']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount', 'currency',
            'billing_name', 'billing_address', 'billing_city',
            'billing_country', 'billing_zip_code',
            'items', 'created_at', 'paid_at',
        ]
        read_only_fields = ['order_number', 'status', 'paid_at']


class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField())
    billing_name = serializers.CharField(max_length=200)
    billing_address = serializers.CharField()
    billing_city = serializers.CharField(max_length=100)
    billing_zip_code = serializers.CharField(max_length=20, required=False, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        for item in value:
            if 'product_id' not in item or 'license_type' not in item:
                raise serializers.ValidationError(
                    "Each item must have product_id and license_type."
                )
        return value


class LicenseSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = [
            'id', 'product', 'product_name', 'license_key', 'license_type',
            'starts_at', 'expires_at', 'is_active',
            'max_activations', 'current_activations',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_product_name(self, obj):
        return getattr(obj.product, f'name_{self._get_lang()}', obj.product.name_tr)
