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
