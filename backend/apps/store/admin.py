from django.contrib import admin
from .models import ProductCategory, Product, Order, OrderItem, License


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name_en',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'unit_price', 'license_type')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'product_type', 'category', 'price_monthly', 'price_yearly', 'price_one_time', 'is_active', 'is_featured')
    list_filter = ('product_type', 'category', 'is_active', 'is_featured')
    list_editable = ('is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name_en',)}
    search_fields = ('name_tr', 'name_en')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'currency', 'paid_at', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('order_number', 'user__email', 'billing_name')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'iyzico_payment_id', 'iyzico_conversation_id')


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_key', 'user', 'product', 'license_type', 'is_active', 'starts_at', 'expires_at')
    list_filter = ('license_type', 'is_active')
    search_fields = ('license_key', 'user__email', 'product__name_tr')
    readonly_fields = ('license_key',)
