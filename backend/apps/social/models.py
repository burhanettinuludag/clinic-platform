"""
Social Media Automation Models.
Hesap baglantilari, kampanyalar, postlar ve yayinlama loglari.
"""

from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class SocialAccount(TimeStampedModel):
    """Bagli sosyal medya hesabi."""

    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    ]
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('expired', 'Token Suresi Dolmus'),
        ('disconnected', 'Baglanti Kesildi'),
        ('pending_review', 'App Review Bekliyor'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=200, help_text='Hesap adi / sayfa adi')
    account_id = models.CharField(max_length=200, help_text='Platform hesap ID')

    # Token bilgileri
    access_token = models.TextField(help_text='Access token')
    refresh_token = models.TextField(blank=True, default='')
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Platform-specific metadata
    page_id = models.CharField(max_length=200, blank=True, default='', help_text='Facebook Page ID (Instagram icin)')
    organization_urn = models.CharField(max_length=200, blank=True, default='', help_text='LinkedIn Organization URN')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    connected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Istatistikler
    total_posts_published = models.PositiveIntegerField(default=0)
    followers_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['platform', 'account_name']
        unique_together = ['platform', 'account_id']
        verbose_name = 'Sosyal Medya Hesabi'
        verbose_name_plural = 'Sosyal Medya Hesaplari'

    def __str__(self):
        return f"{self.get_platform_display()}: {self.account_name}"

    @property
    def is_token_valid(self):
        if not self.token_expires_at:
            return True
        from django.utils import timezone
        return self.token_expires_at > timezone.now()


class SocialCampaign(TimeStampedModel):
    """Haftalik/temali icerik kampanyasi — birden fazla post'u gruplar."""

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('generating', 'AI Uretiyor'),
        ('review', 'Onay Bekliyor'),
        ('partially_approved', 'Kismen Onayli'),
        ('approved', 'Tumu Onayli'),
        ('scheduled', 'Zamanlandi'),
        ('in_progress', 'Yayinlaniyor'),
        ('completed', 'Tamamlandi'),
        ('archived', 'Arsiv'),
    ]

    title = models.CharField(max_length=200)
    theme = models.CharField(max_length=300, help_text='Ana tema')
    description = models.TextField(blank=True, default='')

    # Konfigurasyon
    platforms = models.JSONField(default=list, help_text='["instagram", "linkedin"]')
    posts_per_platform = models.PositiveIntegerField(default=3)
    language = models.CharField(max_length=5, default='tr')
    tone = models.CharField(max_length=20, default='educational')
    target_audience = models.CharField(max_length=30, default='patients')
    week_start = models.DateField(null=True, blank=True)

    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # AI ciktilari (ham)
    content_output = models.JSONField(default=dict, blank=True)
    schedule_output = models.JSONField(default=dict, blank=True)

    # Metrikler
    total_tokens = models.PositiveIntegerField(default=0)
    total_cost_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sosyal Medya Kampanyasi'
        verbose_name_plural = 'Sosyal Medya Kampanyalari'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"

    @property
    def post_stats(self):
        posts = self.posts.all()
        return {
            'total': posts.count(),
            'draft': posts.filter(status='draft').count(),
            'review': posts.filter(status='review').count(),
            'approved': posts.filter(status='approved').count(),
            'scheduled': posts.filter(status='scheduled').count(),
            'published': posts.filter(status='published').count(),
            'failed': posts.filter(status='failed').count(),
        }


class SocialPost(TimeStampedModel):
    """Tek bir sosyal medya postu."""

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('generating', 'AI Uretiyor'),
        ('review', 'Onay Bekliyor'),
        ('approved', 'Onaylandi'),
        ('scheduled', 'Zamanlandi'),
        ('publishing', 'Yayinlaniyor'),
        ('published', 'Yayinlandi'),
        ('failed', 'Basarisiz'),
        ('archived', 'Arsivlendi'),
    ]
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    ]
    FORMAT_CHOICES = [
        ('single_image', 'Tek Gorsel'),
        ('carousel', 'Carousel / Galeri'),
        ('video', 'Video'),
        ('text_only', 'Sadece Metin'),
        ('reel', 'Reel'),
        ('story', 'Story'),
    ]

    # Icerik
    campaign = models.ForeignKey(SocialCampaign, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    post_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='single_image')

    # Metin
    caption_tr = models.TextField(help_text='Turkce post metni')
    caption_en = models.TextField(blank=True, default='', help_text='Ingilizce post metni')
    hashtags = models.JSONField(default=list, help_text='["#norosera", "#noroloji"]')

    # Gorseller
    image_urls = models.JSONField(default=list, help_text='Gorsel URL listesi')
    image_prompt = models.TextField(blank=True, default='', help_text='AI gorsel uretim prompt\'u')
    visual_brief = models.JSONField(default=dict, blank=True, help_text='Gorsel brief detaylari')

    # Zamanlama
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text='Yayinlanma zamani')
    published_at = models.DateTimeField(null=True, blank=True)

    # Durum
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.SET_NULL, null=True, blank=True)

    # Platform response
    platform_post_id = models.CharField(max_length=200, blank=True, default='', help_text='Instagram/LinkedIn post ID')
    platform_url = models.URLField(blank=True, default='', help_text='Yayinlanan post URL')
    publish_error = models.TextField(blank=True, default='')

    # Duzenleme
    edited_caption = models.TextField(blank=True, default='', help_text='Admin tarafindan duzenlenmis metin')
    editor_notes = models.TextField(blank=True, default='')

    # AI metadata
    ai_generated = models.BooleanField(default=True)
    tokens_used = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-scheduled_at', '-created_at']
        verbose_name = 'Sosyal Medya Postu'
        verbose_name_plural = 'Sosyal Medya Postlari'
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['platform', 'status']),
        ]

    def __str__(self):
        return f"[{self.get_platform_display()}] {self.caption_tr[:50]}..."

    @property
    def final_caption(self):
        """Duzenlenmis varsa onu, yoksa orijinali dondur."""
        return self.edited_caption or self.caption_tr

    @property
    def final_caption_with_hashtags(self):
        caption = self.final_caption
        if self.hashtags:
            caption += '\n\n' + ' '.join(self.hashtags)
        return caption


class PublishLog(TimeStampedModel):
    """Yayinlama islemi log kaydi."""

    post = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='publish_logs')
    action = models.CharField(max_length=50)
    success = models.BooleanField(default=False)
    response_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Yayinlama Logu'
        verbose_name_plural = 'Yayinlama Loglari'

    def __str__(self):
        status_str = 'OK' if self.success else 'FAIL'
        return f"[{status_str}] {self.action} - Post #{str(self.post_id)[:8]}"
