from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class ContentCategory(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Content categories'

    def __str__(self):
        return self.name_en


class Article(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    slug = models.SlugField(unique=True, max_length=200)
    title_tr = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    excerpt_tr = models.TextField(blank=True, default='')
    excerpt_en = models.TextField(blank=True, default='')
    body_tr = models.TextField()
    body_en = models.TextField()
    category = models.ForeignKey(
        ContentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    featured_image = models.ImageField(upload_to='articles/', blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_articles',
    )
    doctor_author = models.ForeignKey(
        'accounts.DoctorAuthor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        help_text='DoctorAuthor profili (E-E-A-T ve istatistik icin)',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    seo_title_tr = models.CharField(max_length=200, blank=True, default='')
    seo_title_en = models.CharField(max_length=200, blank=True, default='')
    seo_description_tr = models.TextField(blank=True, default='')
    seo_description_en = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title_en


class EducationItem(TimeStampedModel):
    class ContentType(models.TextChoices):
        VIDEO = 'video', 'Video'
        TEXT = 'text', 'Text'
        INFOGRAPHIC = 'infographic', 'Infographic'
        INTERACTIVE = 'interactive', 'Interactive'

    slug = models.SlugField(unique=True, max_length=200)
    title_tr = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    body_tr = models.TextField(blank=True, default='')
    body_en = models.TextField(blank=True, default='')
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    video_url = models.URLField(blank=True, default='')
    image = models.ImageField(upload_to='education/', blank=True)
    disease_module = models.ForeignKey(
        'patients.DiseaseModule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='education_items',
    )
    category = models.ForeignKey(
        ContentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='education_items',
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    estimated_duration_minutes = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ['disease_module', 'order']

    def __str__(self):
        return self.title_en


class EducationProgress(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='education_progress',
    )
    education_item = models.ForeignKey(
        EducationItem,
        on_delete=models.CASCADE,
        related_name='progress_records',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ['patient', 'education_item']

    def __str__(self):
        return f"{self.patient} - {self.education_item}: {self.progress_percent}%"



class NewsArticle(TimeStampedModel):
    """Noroloji haberleri - FDA onaylari, klinik calismalar, yeni cihazlar."""

    CATEGORY_CHOICES = [
        ('fda_approval', 'FDA Onayi'),
        ('ema_approval', 'EMA Onayi'),
        ('turkey_approval', 'Turkiye Ruhsat'),
        ('clinical_trial', 'Klinik Calisma Sonucu'),
        ('new_device', 'Yeni Cihaz / Teknoloji'),
        ('congress', 'Kongre Haberi'),
        ('turkey_news', 'Turkiye Guncel'),
        ('popular_science', 'Populer Bilim'),
        ('drug_update', 'Ilac Guncellemesi'),
        ('guideline_update', 'Kilavuz Guncellemesi'),
    ]

    PRIORITY_CHOICES = [
        ('urgent', 'Acil'),
        ('high', 'Yuksek'),
        ('medium', 'Orta'),
        ('low', 'Dusuk'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('review', 'Incelemede'),
        ('revision', 'Duzeltme Bekliyor'),
        ('approved', 'Onaylandi'),
        ('published', 'Yayinda'),
        ('archived', 'Arsivlendi'),
    ]

    slug = models.SlugField(unique=True, max_length=350)
    title_tr = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300, blank=True, default='')
    excerpt_tr = models.TextField(max_length=500, blank=True, default='')
    excerpt_en = models.TextField(max_length=500, blank=True, default='')
    body_tr = models.TextField()
    body_en = models.TextField(blank=True, default='')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    source_urls = models.JSONField(default=list, blank=True)
    original_source = models.CharField(max_length=200, blank=True, default='')
    related_diseases = models.ManyToManyField('patients.DiseaseModule', blank=True, related_name='news_articles')
    related_products = models.ManyToManyField('store.Product', blank=True, related_name='news_articles')
    meta_title = models.CharField(max_length=70, blank=True, default='')
    meta_description = models.CharField(max_length=160, blank=True, default='')
    keywords = models.JSONField(default=list, blank=True)
    schema_markup = models.JSONField(default=dict, blank=True)
    featured_image = models.ImageField(upload_to='news_images/', blank=True)
    featured_image_alt = models.CharField(max_length=200, blank=True, default='')
    is_auto_generated = models.BooleanField(default=False)
    author = models.ForeignKey('accounts.DoctorAuthor', null=True, blank=True, on_delete=models.SET_NULL, related_name='news_articles')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_news')
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Haber'
        verbose_name_plural = 'Haberler'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title_tr[:50]}"


class ArticleReview(TimeStampedModel):
    """Yazi degerlendirmesi - ajan veya editor tarafindan."""

    REVIEW_TYPES = [
        ('agent', 'Ajan Degerlendirmesi'),
        ('editor', 'Editor Degerlendirmesi'),
        ('chief_editor', 'Bas Editor Degerlendirmesi'),
    ]

    DECISION_CHOICES = [
        ('publish', 'Yayinla'),
        ('revise', 'Duzeltme Gerekli'),
        ('reject', 'Reddet'),
    ]

    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.CASCADE, related_name='reviews')
    news_article = models.ForeignKey(NewsArticle, null=True, blank=True, on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=15, choices=REVIEW_TYPES)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    medical_accuracy_score = models.IntegerField(default=0)
    language_quality_score = models.IntegerField(default=0)
    seo_score = models.IntegerField(default=0)
    style_compliance_score = models.IntegerField(default=0)
    ethics_score = models.IntegerField(default=0)
    overall_score = models.IntegerField(default=0)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    feedback = models.TextField(blank=True, default='')
    internal_notes = models.TextField(blank=True, default='')
    detailed_analysis = models.JSONField(default=dict, blank=True)
    promotion_flags = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Yazi Degerlendirmesi'
        verbose_name_plural = 'Yazi Degerlendirmeleri'
        ordering = ['-created_at']

    def __str__(self):
        target = self.article or self.news_article
        return f"{self.get_review_type_display()} - {target} ({self.overall_score})"
