from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class SleepCategory(TimeStampedModel):
    """Uyku konulari kategorileri: Uyku Bozukluklari, Uyku Hijyeni, Tani Yontemleri vb."""

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
        verbose_name = 'Sleep Category'
        verbose_name_plural = 'Sleep Categories'

    def __str__(self):
        return self.name_tr


class SleepArticle(TimeStampedModel):
    """Uyku sagligi makaleleri - ucretsiz, herkese acik."""

    class ArticleType(models.TextChoices):
        GENERAL = 'general', 'Genel Bilgi'
        DISORDER = 'disorder', 'Uyku Bozuklugu'
        HYGIENE = 'hygiene', 'Uyku Hijyeni'
        DIAGNOSIS = 'diagnosis', 'Tani Yontemi'
        DISEASE_SLEEP = 'disease_sleep', 'Hastalikta Uyku'
        TIP = 'tip', 'Pratik Oneri'

    category = models.ForeignKey(
        SleepCategory,
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

    # İliskili hastalik (opsiyonel - hastalikta uyku makaleleri icin)
    related_disease = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='migraine, epilepsy, alzheimer, parkinson, diabetes, adhd',
    )

    # Gorseller
    cover_image = models.ImageField(
        upload_to='sleep/covers/',
        blank=True,
        null=True,
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
        help_text='Kaynak ve referanslar (her satir bir referans)',
    )

    author_name = models.CharField(
        max_length=100,
        blank=True,
        default='Norosera Editoryel Ekibi',
    )

    class Meta:
        ordering = ['category__order', 'order', '-created_at']
        verbose_name = 'Sleep Article'
        verbose_name_plural = 'Sleep Articles'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['article_type']),
            models.Index(fields=['related_disease']),
            models.Index(fields=['is_published', '-created_at']),
        ]

    def __str__(self):
        return self.title_tr


class SleepTip(TimeStampedModel):
    """Gunluk uyku onerileri - kisa ve pratik."""

    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    content_tr = models.TextField(max_length=500)
    content_en = models.TextField(max_length=500)
    icon = models.CharField(max_length=50, blank=True, default='moon')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Sleep Tip'
        verbose_name_plural = 'Sleep Tips'

    def __str__(self):
        return self.title_tr


class SleepFAQ(TimeStampedModel):
    """Sikca sorulan sorular."""

    category = models.ForeignKey(
        SleepCategory,
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
        verbose_name = 'Sleep FAQ'
        verbose_name_plural = 'Sleep FAQs'

    def __str__(self):
        return self.question_tr


# ── Uyku Farkındalık Testleri ──────────────────────────────────────────

class SleepScreeningTest(TimeStampedModel):
    """Uyku farkındalık testi (telif sorunu olmayan özgün anketler)."""

    slug = models.SlugField(unique=True)
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_tr = models.TextField()
    description_en = models.TextField()
    instructions_tr = models.TextField(blank=True, default='')
    instructions_en = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='clipboard-list')
    duration_minutes = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Sleep Screening Test'
        verbose_name_plural = 'Sleep Screening Tests'

    def __str__(self):
        return self.title_tr

    @property
    def question_count(self):
        return self.questions.count()


class SleepScreeningQuestion(TimeStampedModel):
    """Farkındalık testi sorusu."""

    test = models.ForeignKey(
        SleepScreeningTest,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_tr = models.CharField(max_length=500)
    question_en = models.CharField(max_length=500)
    help_text_tr = models.CharField(max_length=500, blank=True, default='')
    help_text_en = models.CharField(max_length=500, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Screening Question'
        verbose_name_plural = 'Screening Questions'

    def __str__(self):
        return f"{self.test.slug} - Q{self.order}: {self.question_tr[:60]}"


class SleepScreeningOption(TimeStampedModel):
    """Soru seçeneği ve puanı."""

    question = models.ForeignKey(
        SleepScreeningQuestion,
        on_delete=models.CASCADE,
        related_name='options',
    )
    text_tr = models.CharField(max_length=300)
    text_en = models.CharField(max_length=300)
    score = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Screening Option'
        verbose_name_plural = 'Screening Options'

    def __str__(self):
        return f"{self.text_tr[:50]} ({self.score}p)"


class SleepScreeningResultRange(TimeStampedModel):
    """Test sonuç aralıkları ve yorumları."""

    class Level(models.TextChoices):
        LOW = 'low', 'Düşük Risk'
        MODERATE = 'moderate', 'Orta Risk'
        HIGH = 'high', 'Yüksek Risk'
        SEVERE = 'severe', 'Çok Yüksek Risk'

    test = models.ForeignKey(
        SleepScreeningTest,
        on_delete=models.CASCADE,
        related_name='result_ranges',
    )
    level = models.CharField(max_length=20, choices=Level.choices)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    title_tr = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_tr = models.TextField()
    description_en = models.TextField()
    recommendation_tr = models.TextField(blank=True, default='')
    recommendation_en = models.TextField(blank=True, default='')
    color = models.CharField(
        max_length=30,
        default='green',
        help_text='Tailwind renk adı: green, yellow, orange, red',
    )

    class Meta:
        ordering = ['min_score']
        verbose_name = 'Screening Result Range'
        verbose_name_plural = 'Screening Result Ranges'

    def __str__(self):
        return f"{self.test.slug}: {self.min_score}-{self.max_score} → {self.level}"
