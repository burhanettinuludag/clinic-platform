import uuid
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=100)
    resource_id = models.UUIDField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        return f"{self.action} on {self.resource_type} by {self.user}"


class ConsentRecord(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consent_records',
    )
    consent_type = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ['user', 'consent_type', 'version']
        ordering = ['-created_at']

    def __str__(self):
        status = 'granted' if self.granted else 'revoked'
        return f"{self.consent_type} v{self.version} - {status}"


class SiteConfig(TimeStampedModel):
    """Admin'den degistirilebilir anahtar-deger sistem parametreleri."""

    class ValueType(models.TextChoices):
        STRING = 'string', 'String'
        INTEGER = 'integer', 'Integer'
        FLOAT = 'float', 'Float'
        BOOLEAN = 'boolean', 'Boolean'
        JSON = 'json', 'JSON'

    key = models.SlugField(max_length=100, unique=True)
    label = models.CharField(max_length=200, help_text='Admin panelinde gorunecek isim')
    value = models.TextField(default='')
    value_type = models.CharField(max_length=10, choices=ValueType.choices, default=ValueType.STRING)
    description = models.TextField(blank=True, default='', help_text='Parametre aciklamasi')
    category = models.CharField(
        max_length=50,
        default='general',
        help_text='Gruplama icin kategori',
    )
    is_public = models.BooleanField(
        default=False,
        help_text='True ise frontend API uzerinden erisilebilir',
    )

    class Meta:
        ordering = ['category', 'key']
        verbose_name = 'Site Config'
        verbose_name_plural = 'Site Configs'

    def __str__(self):
        return f"{self.key} = {self.value[:50]}"

    def get_typed_value(self):
        if self.value_type == self.ValueType.BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes', 'evet')
        elif self.value_type == self.ValueType.INTEGER:
            return int(self.value) if self.value else 0
        elif self.value_type == self.ValueType.FLOAT:
            return float(self.value) if self.value else 0.0
        elif self.value_type == self.ValueType.JSON:
            import json
            return json.loads(self.value) if self.value else {}
        return self.value


class FeatureFlag(TimeStampedModel):
    """Ozellikleri acip kapatmak icin bayraklar."""

    key = models.SlugField(max_length=100, unique=True)
    label = models.CharField(max_length=200, help_text='Ozellik ismi')
    is_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    enabled_for_roles = models.JSONField(
        default=list, blank=True,
        help_text='Bos ise herkese acik. ["patient","doctor"] gibi roller belirtilebilir.',
    )

    class Meta:
        ordering = ['key']
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'

    def __str__(self):
        status = 'ON' if self.is_enabled else 'OFF'
        return f"{self.key} [{status}]"

    def is_enabled_for(self, user=None):
        if not self.is_enabled:
            return False
        if not self.enabled_for_roles:
            return True
        if user and hasattr(user, 'role'):
            return user.role in self.enabled_for_roles
        return False



class AgentTask(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('running', 'Calisiyor'),
        ('completed', 'Tamamlandi'),
        ('failed', 'Basarisiz'),
        ('skipped', 'Atlandi'),
        ('cancelled', 'Iptal Edildi'),
    ]
    TASK_TYPES = [
        ('generate_content', 'Icerik Uret'),
        ('generate_news', 'Haber Uret'),
        ('optimize_seo', 'SEO Optimize'),
        ('check_quality', 'Kalite Kontrol'),
        ('review_article', 'Yazi Degerlendir'),
        ('find_media', 'Gorsel Bul'),
        ('add_links', 'Link Ekle'),
        ('edit_content', 'Icerik Duzenle'),
        ('scan_trends', 'Trend Tara'),
        ('analyze_competitor', 'Rakip Analiz'),
        ('full_pipeline', 'Tam Pipeline'),
        ('legal_check', 'Hukuki Kontrol'),
        ('translate', 'Ceviri'),
    ]
    agent_name = models.CharField(max_length=50)
    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, default='')
    retry_count = models.PositiveIntegerField(default=0)
    tokens_used = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    llm_provider = models.CharField(max_length=20, blank=True, default='')
    llm_model = models.CharField(max_length=50, blank=True, default='')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='agent_tasks')
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    article_id = models.UUIDField(null=True, blank=True)
    news_article_id = models.UUIDField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Ajan Gorevi'
        verbose_name_plural = 'Ajan Gorevleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_name', 'status']),
            models.Index(fields=['task_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.agent_name} - {self.get_task_type_display()} ({self.get_status_display()})"

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, output_data, tokens=0, duration=0, provider='', model_name=''):
        from django.utils import timezone
        self.status = 'completed'
        self.output_data = output_data
        self.tokens_used = tokens
        self.duration_ms = duration
        self.llm_provider = provider
        self.llm_model = model_name
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        from django.utils import timezone
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
