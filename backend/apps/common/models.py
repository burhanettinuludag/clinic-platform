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


class Announcement(TimeStampedModel):
    """Site geneli duyuru bandi. Anasayfa ustunde gorunur."""
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default='')
    message_tr = models.TextField(max_length=500)
    message_en = models.TextField(max_length=500, blank=True, default='')
    link_url = models.URLField(blank=True, default='')
    link_text_tr = models.CharField(max_length=50, blank=True, default='')
    link_text_en = models.CharField(max_length=50, blank=True, default='')
    bg_color = models.CharField(max_length=7, default='#1B4F72', help_text='HEX renk kodu')
    text_color = models.CharField(max_length=7, default='#FFFFFF')
    is_active = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0, help_text='Yuksek = once gosterilir')
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Duyuru'
        verbose_name_plural = 'Duyurular'

    def __str__(self):
        icon = '\U0001f7e2' if self.is_active else '\U0001f534'
        return f"{icon} {self.title_tr}"


class HomepageHero(TimeStampedModel):
    """Anasayfa hero section ayarlari."""
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default='')
    subtitle_tr = models.TextField(max_length=500)
    subtitle_en = models.TextField(max_length=500, blank=True, default='')
    cta_text_tr = models.CharField(max_length=50, default='Hemen Basla')
    cta_text_en = models.CharField(max_length=50, default='Get Started')
    cta_url = models.CharField(max_length=200, default='/auth/register')
    secondary_cta_text_tr = models.CharField(max_length=50, blank=True, default='')
    secondary_cta_text_en = models.CharField(max_length=50, blank=True, default='')
    secondary_cta_url = models.CharField(max_length=200, blank=True, default='')
    background_image = models.ImageField(upload_to='hero/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Anasayfa Hero'
        verbose_name_plural = 'Anasayfa Hero'
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return self.title_tr


class SocialLink(TimeStampedModel):
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter / X'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('github', 'GitHub'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Sosyal Medya'

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


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
        ('marketing_content', 'Pazarlama Icerik'),
        ('visual_brief', 'Gorsel Brief'),
        ('schedule_plan', 'Yayin Plani'),
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


class BrokenLink(TimeStampedModel):
    """Kirik link kayitlari. Crawler tarafindan tespit edilir."""

    class Status(models.TextChoices):
        DETECTED = 'detected', 'Tespit Edildi'
        AUTO_FIXED = 'auto_fixed', 'Otomatik Tamir'
        AI_SUGGESTED = 'ai_suggested', 'AI Onerisi Var'
        MANUALLY_FIXED = 'manually_fixed', 'Manuel Tamir'
        IGNORED = 'ignored', 'Yok Sayildi'

    class SourceType(models.TextChoices):
        ARTICLE = 'article', 'Blog Yazisi'
        NEWS = 'news', 'Haber'
        EDUCATION = 'education', 'Egitim Icerigi'
        ANNOUNCEMENT = 'announcement', 'Duyuru'
        SOCIAL_LINK = 'social_link', 'Sosyal Medya'

    class LinkType(models.TextChoices):
        INTERNAL = 'internal', 'Dahili'
        EXTERNAL = 'external', 'Harici'
        IMAGE = 'image', 'Gorsel'
        VIDEO = 'video', 'Video'

    broken_url = models.URLField(max_length=2000)
    http_status = models.IntegerField(null=True, blank=True, help_text='HTTP yanit kodu (404, 500, vb.)')
    error_message = models.CharField(max_length=500, blank=True, default='')
    link_type = models.CharField(max_length=10, choices=LinkType.choices, default=LinkType.EXTERNAL)

    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    source_id = models.UUIDField(help_text='Kaynak icerigin UUID si')
    source_title = models.CharField(max_length=300, blank=True, default='')
    source_field = models.CharField(max_length=50, help_text='Linkin bulundugu alan (body_tr, video_url, vb.)')
    source_language = models.CharField(max_length=5, blank=True, default='')

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DETECTED)
    suggested_url = models.URLField(max_length=2000, blank=True, default='')
    fix_notes = models.TextField(blank=True, default='')
    fixed_at = models.DateTimeField(null=True, blank=True)
    fixed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='fixed_links',
    )

    last_checked = models.DateTimeField(auto_now=True)
    check_count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kirik Link'
        verbose_name_plural = 'Kirik Linkler'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['source_type', 'source_id']),
        ]
        unique_together = ['broken_url', 'source_type', 'source_id', 'source_field']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.broken_url[:80]} ({self.http_status or 'N/A'})"


class BrokenLinkScan(TimeStampedModel):
    """Tarama oturumu. Her crawler calismasini kaydeder."""

    class Status(models.TextChoices):
        RUNNING = 'running', 'Calisiyor'
        COMPLETED = 'completed', 'Tamamlandi'
        FAILED = 'failed', 'Basarisiz'

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.RUNNING)
    total_links_checked = models.PositiveIntegerField(default=0)
    broken_links_found = models.PositiveIntegerField(default=0)
    auto_fixed_count = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Link Taramasi'
        verbose_name_plural = 'Link Taramalari'

    def __str__(self):
        return f"Tarama {self.created_at:%Y-%m-%d %H:%M} - {self.broken_links_found} kirik link"


class MarketingCampaign(TimeStampedModel):
    """Haftalik marketing icerik paketi."""

    STATUS_CHOICES = [
        ('generating', 'Uretiyor'),
        ('review', 'Inceleme Bekliyor'),
        ('approved', 'Onaylandi'),
        ('scheduled', 'Planlandi'),
        ('published', 'Yayinlandi'),
        ('archived', 'Arsivlendi'),
    ]

    title = models.CharField(max_length=200, help_text='Kampanya basligi')
    theme = models.CharField(max_length=300, help_text='Ana tema')
    week_start = models.DateField(help_text='Hafta baslangici')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='generating')
    platforms = models.JSONField(default=list, help_text='["instagram", "linkedin", "twitter"]')
    language = models.CharField(max_length=5, default='tr')
    tone = models.CharField(max_length=20, default='educational')
    target_audience = models.CharField(max_length=20, default='patients')

    # Agent ciktilari
    content_output = models.JSONField(default=dict, blank=True, help_text='Marketing Content Agent ciktisi')
    visual_briefs = models.JSONField(default=dict, blank=True, help_text='Visual Brief Agent ciktisi')
    schedule = models.JSONField(default=dict, blank=True, help_text='Scheduling Agent ciktisi')

    # Duzenleme
    edited_content = models.JSONField(default=dict, blank=True, help_text='Admin tarafindan duzenlenmis icerik')
    editor_notes = models.TextField(blank=True, default='')

    # Meta
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='marketing_campaigns',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    total_tokens = models.PositiveIntegerField(default=0)
    total_cost_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    pipeline_task = models.ForeignKey(
        AgentTask, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='marketing_campaigns',
    )

    class Meta:
        ordering = ['-week_start', '-created_at']
        verbose_name = 'Marketing Kampanyasi'
        verbose_name_plural = 'Marketing Kampanyalari'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} ({self.week_start})"
