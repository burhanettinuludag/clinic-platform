from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Payment(TimeStampedModel):
    class PaymentStatus(models.TextChoices):
        INIT = 'init', 'Initialized'
        SUCCESS = 'success', 'Success'
        FAILURE = 'failure', 'Failure'
        REFUND = 'refund', 'Refunded'

    order = models.ForeignKey(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='payments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.INIT,
    )
    iyzico_payment_id = models.CharField(max_length=100, blank=True, default='')
    iyzico_token = models.CharField(max_length=200, blank=True, default='')
    card_last_four = models.CharField(max_length=4, blank=True, default='')
    card_type = models.CharField(max_length=50, blank=True, default='')
    installment = models.PositiveSmallIntegerField(default=1)
    raw_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.status}"


class Subscription(TimeStampedModel):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PENDING = 'pending', 'Pending'
        UNPAID = 'unpaid', 'Unpaid'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    product = models.ForeignKey(
        'store.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions',
    )
    license = models.OneToOneField(
        'store.License',
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscription',
    )
    iyzico_subscription_reference = models.CharField(max_length=100, blank=True, default='')
    iyzico_customer_reference = models.CharField(max_length=100, blank=True, default='')
    plan_type = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.PENDING,
    )
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Subscription {self.id} - {self.status}"
