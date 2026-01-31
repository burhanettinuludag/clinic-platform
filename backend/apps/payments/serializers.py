from rest_framework import serializers
from .models import Payment, Subscription


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'currency', 'status',
            'card_last_four', 'card_type', 'installment',
            'error_message', 'created_at',
        ]
        read_only_fields = fields


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    callback_url = serializers.URLField(required=False)


class PaymentCallbackSerializer(serializers.Serializer):
    token = serializers.CharField()


class SubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'product', 'product_name', 'plan_type', 'status',
            'current_period_start', 'current_period_end',
            'cancelled_at', 'created_at',
        ]
        read_only_fields = fields

    def get_product_name(self, obj):
        if not obj.product:
            return ''
        lang = self._get_lang()
        return getattr(obj.product, f'name_{lang}', obj.product.name_tr)

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'
