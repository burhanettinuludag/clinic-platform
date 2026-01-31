from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from apps.store.models import Order, License
from .models import Payment, Subscription
from .serializers import (
    PaymentSerializer,
    InitiatePaymentSerializer,
    PaymentCallbackSerializer,
    SubscriptionSerializer,
)
from .services import iyzico_service


class InitiatePaymentView(generics.GenericAPIView):
    """Odeme baslatma: iyzico checkout form olusturur."""
    permission_classes = [IsAuthenticated]
    serializer_class = InitiatePaymentSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(
            Order, id=serializer.validated_data['order_id'], user=request.user
        )

        if order.status != Order.OrderStatus.PENDING:
            return Response(
                {'error': 'Bu siparis icin odeme yapilamaz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_amount,
            currency=order.currency,
            status=Payment.PaymentStatus.INIT,
        )

        callback_url = serializer.validated_data.get(
            'callback_url',
            f'{request.scheme}://{request.get_host()}/api/v1/payments/callback/',
        )

        result = iyzico_service.create_checkout_form(order, request.user, callback_url)

        if result.get('status') == 'success':
            payment.iyzico_token = result.get('token', '')
            payment.raw_response = result
            payment.save()

            order.status = Order.OrderStatus.PROCESSING
            order.iyzico_conversation_id = str(order.id)[:20]
            order.save()

            return Response({
                'payment_id': str(payment.id),
                'checkout_form_content': result.get('checkoutFormContent'),
                'token': result.get('token'),
                'token_expire_time': result.get('tokenExpireTime'),
            })
        else:
            payment.status = Payment.PaymentStatus.FAILURE
            payment.error_message = result.get('errorMessage', 'Bilinmeyen hata')
            payment.raw_response = result
            payment.save()

            return Response(
                {'error': result.get('errorMessage', 'Odeme baslatilamadi')},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentCallbackView(generics.GenericAPIView):
    """iyzico odeme callback."""
    permission_classes = [AllowAny]
    serializer_class = PaymentCallbackSerializer

    def post(self, request):
        token = request.data.get('token') or request.query_params.get('token')
        if not token:
            return Response({'error': 'Token bulunamadi'}, status=status.HTTP_400_BAD_REQUEST)

        result = iyzico_service.retrieve_checkout_form(token)

        try:
            payment = Payment.objects.get(iyzico_token=token)
        except Payment.DoesNotExist:
            return Response({'error': 'Odeme bulunamadi'}, status=status.HTTP_404_NOT_FOUND)

        order = payment.order

        if result.get('paymentStatus') == 'SUCCESS':
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.iyzico_payment_id = result.get('paymentId', '')
            payment.card_last_four = result.get('lastFourDigits', '')
            payment.card_type = result.get('cardType', '')
            payment.installment = result.get('installment', 1)
            payment.raw_response = result
            payment.save()

            order.status = Order.OrderStatus.COMPLETED
            order.iyzico_payment_id = result.get('paymentId', '')
            order.paid_at = timezone.now()
            order.save()

            self._create_licenses(order)

            return Response({'status': 'success', 'order_number': order.order_number})
        else:
            payment.status = Payment.PaymentStatus.FAILURE
            payment.error_message = result.get('errorMessage', 'Odeme basarisiz')
            payment.raw_response = result
            payment.save()

            order.status = Order.OrderStatus.FAILED
            order.save()

            return Response(
                {'status': 'failure', 'error': result.get('errorMessage')},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _create_licenses(self, order):
        now = timezone.now()
        for item in order.items.select_related('product'):
            if item.product:
                license_type_map = {
                    'monthly': 'monthly',
                    'yearly': 'yearly',
                    'one_time': 'lifetime',
                }
                expires_map = {
                    'monthly': now + timedelta(days=30),
                    'yearly': now + timedelta(days=365),
                    'one_time': None,
                }
                License.objects.create(
                    user=order.user,
                    product=item.product,
                    order_item=item,
                    license_type=license_type_map.get(item.license_type, 'lifetime'),
                    starts_at=now,
                    expires_at=expires_map.get(item.license_type),
                    is_active=True,
                )


class PaymentHistoryView(generics.ListAPIView):
    """Kullanicinin odeme gecmisi."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanicinin abonelikleri."""
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related('product')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        if subscription.status == Subscription.SubscriptionStatus.CANCELLED:
            return Response(
                {'error': 'Abonelik zaten iptal edilmis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.status = Subscription.SubscriptionStatus.CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.save()
        return Response({'status': 'cancelled'})
