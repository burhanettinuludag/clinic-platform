from django.contrib import admin
from .models import Payment, Subscription


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'amount', 'currency', 'status', 'card_last_four', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__email', 'order__order_number', 'iyzico_payment_id')
    date_hierarchy = 'created_at'
    readonly_fields = ('iyzico_payment_id', 'iyzico_token', 'raw_response')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'plan_type', 'status', 'current_period_start', 'current_period_end')
    list_filter = ('plan_type', 'status')
    search_fields = ('user__email', 'product__name_tr')
    readonly_fields = ('iyzico_subscription_reference', 'iyzico_customer_reference')
