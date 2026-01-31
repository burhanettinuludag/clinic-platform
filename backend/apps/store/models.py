import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class ProductCategory(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Product categories'

    def __str__(self):
        return self.name_en


class Product(TimeStampedModel):
    class ProductType(models.TextChoices):
        SOFTWARE = 'software', 'Software'
        TOOL = 'tool', 'Tool'
        TEMPLATE = 'template', 'Template'
        COURSE = 'course', 'Course'

    slug = models.SlugField(unique=True, max_length=200)
    name_tr = models.CharField(max_length=300)
    name_en = models.CharField(max_length=300)
    description_tr = models.TextField()
    description_en = models.TextField()
    short_description_tr = models.CharField(max_length=500, blank=True, default='')
    short_description_en = models.CharField(max_length=500, blank=True, default='')
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    featured_image = models.ImageField(upload_to='products/', blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_one_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='TRY')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    version = models.CharField(max_length=20, blank=True, default='')
    system_requirements = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name_en


class Order(TimeStampedModel):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    billing_name = models.CharField(max_length=200)
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_country = models.CharField(max_length=100, default='Turkey')
    billing_zip_code = models.CharField(max_length=20, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    iyzico_payment_id = models.CharField(max_length=100, blank=True, default='')
    iyzico_conversation_id = models.CharField(max_length=100, blank=True, default='')
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.status}"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )
    product_name = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    license_type = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly'), ('one_time', 'One Time')],
        default='one_time',
    )

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class License(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licenses',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='licenses',
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='license',
    )
    license_key = models.CharField(max_length=100, unique=True)
    license_type = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly'), ('lifetime', 'Lifetime')],
    )
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_activations = models.PositiveIntegerField(default=1)
    current_activations = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-starts_at']
        indexes = [
            models.Index(fields=['user', 'product']),
            models.Index(fields=['license_key']),
        ]

    def save(self, *args, **kwargs):
        if not self.license_key:
            self.license_key = f"LIC-{uuid.uuid4().hex[:16].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_key} - {self.product.name_en}"
