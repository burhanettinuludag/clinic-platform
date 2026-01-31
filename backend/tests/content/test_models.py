"""
Unit tests for content models.
"""

import pytest
from django.utils import timezone
from apps.content.models import (
    ContentCategory,
    Article,
    EducationItem,
    EducationProgress,
)


@pytest.mark.django_db
class TestContentCategory:
    """Tests for ContentCategory model."""

    def test_create_category(self, db):
        """Test creating a content category."""
        category = ContentCategory.objects.create(
            slug='migraine-triggers',
            name_tr='Migren Tetikleyicileri',
            name_en='Migraine Triggers',
            order=1,
        )
        assert category.slug == 'migraine-triggers'
        assert category.name_en == 'Migraine Triggers'

    def test_category_str(self, db):
        """Test category string representation."""
        category = ContentCategory.objects.create(
            slug='test',
            name_tr='Test Kategori',
            name_en='Test Category',
        )
        assert str(category) == 'Test Category'

    def test_nested_category(self, db):
        """Test creating nested (child) category."""
        parent = ContentCategory.objects.create(
            slug='parent',
            name_tr='Ana Kategori',
            name_en='Parent Category',
        )
        child = ContentCategory.objects.create(
            slug='child',
            name_tr='Alt Kategori',
            name_en='Child Category',
            parent=parent,
        )
        assert child.parent == parent
        assert parent.children.first() == child

    def test_unique_slug(self, db):
        """Test slug must be unique."""
        ContentCategory.objects.create(
            slug='unique',
            name_tr='Test',
            name_en='Test',
        )
        with pytest.raises(Exception):
            ContentCategory.objects.create(
                slug='unique',
                name_tr='Test2',
                name_en='Test2',
            )

    def test_ordering(self, db):
        """Test categories are ordered by order field."""
        cat1 = ContentCategory.objects.create(
            slug='second', name_tr='Second', name_en='Second', order=2,
        )
        cat2 = ContentCategory.objects.create(
            slug='first', name_tr='First', name_en='First', order=1,
        )
        categories = list(ContentCategory.objects.all())
        assert categories[0] == cat2
        assert categories[1] == cat1


@pytest.mark.django_db
class TestArticle:
    """Tests for Article model."""

    @pytest.fixture
    def category(self, db):
        """Create a category for testing."""
        return ContentCategory.objects.create(
            slug='health',
            name_tr='Saglik',
            name_en='Health',
        )

    def test_create_article(self, admin_user, category):
        """Test creating an article."""
        article = Article.objects.create(
            slug='migraine-prevention-tips',
            title_tr='Migren Onleme Ipuclari',
            title_en='Migraine Prevention Tips',
            excerpt_tr='Migreni onlemek icin onemli ipuclari',
            excerpt_en='Important tips to prevent migraine',
            body_tr='Migren, hayat kalitesini...',
            body_en='Migraine significantly affects...',
            category=category,
            author=admin_user,
            status='published',
            published_at=timezone.now(),
            is_featured=True,
        )
        assert article.title_en == 'Migraine Prevention Tips'
        assert article.status == 'published'
        assert article.is_featured is True

    def test_article_str(self, admin_user):
        """Test article string representation."""
        article = Article.objects.create(
            slug='test',
            title_tr='Test Makale',
            title_en='Test Article',
            body_tr='Icerik',
            body_en='Content',
            author=admin_user,
        )
        assert str(article) == 'Test Article'

    def test_article_statuses(self, admin_user):
        """Test all article status choices."""
        statuses = ['draft', 'published', 'archived']
        for status in statuses:
            article = Article.objects.create(
                slug=f'test-{status}',
                title_tr=f'Test {status}',
                title_en=f'Test {status}',
                body_tr='Content',
                body_en='Content',
                author=admin_user,
                status=status,
            )
            assert article.status == status

    def test_default_status_is_draft(self, admin_user):
        """Test default article status is draft."""
        article = Article.objects.create(
            slug='draft-test',
            title_tr='Test',
            title_en='Test',
            body_tr='Content',
            body_en='Content',
            author=admin_user,
        )
        assert article.status == 'draft'

    def test_seo_fields(self, admin_user):
        """Test article with SEO fields."""
        article = Article.objects.create(
            slug='seo-test',
            title_tr='Test',
            title_en='Test',
            body_tr='Content',
            body_en='Content',
            author=admin_user,
            seo_title_tr='SEO Baslik',
            seo_title_en='SEO Title',
            seo_description_tr='SEO Aciklama',
            seo_description_en='SEO Description',
        )
        assert article.seo_title_en == 'SEO Title'
        assert article.seo_description_en == 'SEO Description'


@pytest.mark.django_db
class TestEducationItem:
    """Tests for EducationItem model."""

    @pytest.fixture
    def category(self, db):
        """Create a category for testing."""
        return ContentCategory.objects.create(
            slug='education',
            name_tr='Egitim',
            name_en='Education',
        )

    def test_create_education_item(self, disease_module, category):
        """Test creating an education item."""
        item = EducationItem.objects.create(
            slug='understanding-migraine',
            title_tr='Migreni Anlamak',
            title_en='Understanding Migraine',
            body_tr='Migren hakkinda bilgiler...',
            body_en='Information about migraine...',
            content_type='text',
            disease_module=disease_module,
            category=category,
            order=1,
            is_published=True,
            estimated_duration_minutes=10,
        )
        assert item.title_en == 'Understanding Migraine'
        assert item.content_type == 'text'
        assert item.estimated_duration_minutes == 10

    def test_education_item_str(self):
        """Test education item string representation."""
        item = EducationItem.objects.create(
            slug='test',
            title_tr='Test Egitim',
            title_en='Test Education',
            content_type='text',
        )
        assert str(item) == 'Test Education'

    def test_content_types(self):
        """Test all content type choices."""
        types = ['video', 'text', 'infographic', 'interactive']
        for content_type in types:
            item = EducationItem.objects.create(
                slug=f'test-{content_type}',
                title_tr=f'Test {content_type}',
                title_en=f'Test {content_type}',
                content_type=content_type,
            )
            assert item.content_type == content_type

    def test_video_education_item(self):
        """Test education item with video URL."""
        item = EducationItem.objects.create(
            slug='video-test',
            title_tr='Video Egitim',
            title_en='Video Education',
            content_type='video',
            video_url='https://example.com/video.mp4',
        )
        assert item.video_url == 'https://example.com/video.mp4'


@pytest.mark.django_db
class TestEducationProgress:
    """Tests for EducationProgress model."""

    @pytest.fixture
    def education_item(self):
        """Create an education item for testing."""
        return EducationItem.objects.create(
            slug='test-item',
            title_tr='Test',
            title_en='Test',
            content_type='text',
            is_published=True,
        )

    def test_start_education(self, patient_user, education_item):
        """Test starting education progress."""
        progress = EducationProgress.objects.create(
            patient=patient_user,
            education_item=education_item,
            progress_percent=0,
        )
        assert progress.patient == patient_user
        assert progress.progress_percent == 0
        assert progress.completed_at is None

    def test_update_progress(self, patient_user, education_item):
        """Test updating education progress."""
        progress = EducationProgress.objects.create(
            patient=patient_user,
            education_item=education_item,
            progress_percent=50,
        )
        progress.progress_percent = 75
        progress.save()
        progress.refresh_from_db()
        assert progress.progress_percent == 75

    def test_complete_education(self, patient_user, education_item):
        """Test completing education."""
        progress = EducationProgress.objects.create(
            patient=patient_user,
            education_item=education_item,
            progress_percent=100,
            completed_at=timezone.now(),
        )
        assert progress.progress_percent == 100
        assert progress.completed_at is not None

    def test_progress_str(self, patient_user, education_item):
        """Test education progress string representation."""
        progress = EducationProgress.objects.create(
            patient=patient_user,
            education_item=education_item,
            progress_percent=50,
        )
        expected = f"{patient_user} - {education_item}: 50%"
        assert str(progress) == expected

    def test_unique_progress_per_item(self, patient_user, education_item):
        """Test only one progress per patient per item."""
        EducationProgress.objects.create(
            patient=patient_user,
            education_item=education_item,
        )
        with pytest.raises(Exception):
            EducationProgress.objects.create(
                patient=patient_user,
                education_item=education_item,
            )
