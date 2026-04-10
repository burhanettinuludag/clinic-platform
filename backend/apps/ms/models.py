from django.db import models
from apps.common.models import TimeStampedModel


class MSCategory(TimeStampedModel):
    """MS konuları kategorileri: Tanım, Tanı Kriterleri, MR Bulguları vb."""

    slug = models.SlugField(unique=True)
    name_tr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_tr = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'MS Category'
        verbose_name_plural = 'MS Categories'

    def __str__(self):
        return self.name_tr


class MSArticle(TimeStampedModel):
    """Multipl Skleroz bilgi makaleleri - ücretsiz, herkese açık."""

    class ArticleType(models.TextChoices):
        DEFINITION = 'definition', 'Genel Tanım'
        DIAGNOSIS = 'diagnosis', 'Tanı'
        IMAGING = 'imaging', 'Görüntüleme'
        BIOMARKER = 'biomarker', 'Biyobelirteç'
        TREATMENT = 'treatment', 'Tedavi'
        NEW_TREATMENT = 'new_treatment', 'Yeni Tedavi'
        GENERAL = 'general', 'Genel Bilgi'

    category = models.ForeignKey(
        MSCategory,
        on_delete=models.CASCADE,
        related_name='articles',
    )
    slug = models.SlugField(unique=True, max_length=200)
    article_type = models.CharField(
        max_length=20,
        choices=ArticleType.choices,
        default=ArticleType.GENERAL,
    )
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    subtitle_tr = models.CharField(max_length=300, blank=True, default='')
    subtitle_en = models.CharField(max_length=300, blank=True, default='')
    content_tr = models.TextField()
    content_en = models.TextField()
    summary_tr = models.TextField(blank=True, default='', max_length=500)
    summary_en = models.TextField(blank=True, default='', max_length=500)

    # Görseller
    cover_image = models.ImageField(
        upload_to='ms/covers/',
        blank=True,
        null=True,
    )
    cover_image_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        help_text='Harici görsel URL (Unsplash vb.). cover_image boşsa kullanılır.',
    )
    icon = models.CharField(max_length=50, blank=True, default='')

    # Meta
    reading_time_minutes = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    # SEO
    meta_title_tr = models.CharField(max_length=200, blank=True, default='')
    meta_title_en = models.CharField(max_length=200, blank=True, default='')
    meta_description_tr = models.TextField(blank=True, default='', max_length=300)
    meta_description_en = models.TextField(blank=True, default='', max_length=300)

    # Referanslar
    references = models.TextField(
        blank=True,
        default='',
        help_text='Kaynak ve referanslar (her satır bir referans)',
    )

    author_name = models.CharField(
        max_length=100,
        blank=True,
        default='Norosera Editöryal Ekibi',
    )

    class Meta:
        ordering = ['category__order', 'order', '-created_at']
        verbose_name = 'MS Article'
        verbose_name_plural = 'MS Articles'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['article_type']),
            models.Index(fields=['is_published', '-created_at']),
        ]

    def __str__(self):
        return self.title_tr


class MSTip(TimeStampedModel):
    """MS ile yaşam önerileri - kısa ve pratik."""

    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    content_tr = models.TextField(max_length=500)
    content_en = models.TextField(max_length=500)
    icon = models.CharField(max_length=50, blank=True, default='brain')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'MS Tip'
        verbose_name_plural = 'MS Tips'

    def __str__(self):
        return self.title_tr


class MSFAQ(TimeStampedModel):
    """Sıkça sorulan sorular."""

    category = models.ForeignKey(
        MSCategory,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
    )
    question_tr = models.CharField(max_length=300)
    question_en = models.CharField(max_length=300)
    answer_tr = models.TextField()
    answer_en = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'MS FAQ'
        verbose_name_plural = 'MS FAQs'

    def __str__(self):
        return self.question_tr
