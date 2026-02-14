"""
Yazar (DoctorAuthor) islemleri icin serializer'lar.

Kapsam:
- DoctorAuthor profil CRUD
- Yazarin makale yonetimi (Article)
- Yazarin haber yonetimi (NewsArticle)
- Yayin onay akisi (status transitions)
- ArticleReview
"""

from rest_framework import serializers
from django.utils import timezone

from apps.accounts.models import DoctorAuthor, DoctorProfile
from apps.content.models import Article, NewsArticle, ArticleReview


# ─────────────────────────────────────────────
# 1. DoctorAuthor Profil Serializer'lari
# ─────────────────────────────────────────────

class DoctorAuthorListSerializer(serializers.ModelSerializer):
    """Yazar listesi icin kisa bilgi."""
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    specialty_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAuthor
        fields = [
            'id', 'full_name', 'email', 'primary_specialty',
            'specialty_display', 'author_level', 'level_display',
            'total_articles', 'total_views', 'average_rating',
            'is_verified', 'is_active', 'institution',
            'profile_photo',
        ]

    def get_full_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_email(self, obj):
        return obj.doctor.user.email

    def get_specialty_display(self, obj):
        return obj.get_primary_specialty_display()

    def get_level_display(self, obj):
        return obj.get_author_level_display()


class DoctorAuthorDetailSerializer(serializers.ModelSerializer):
    """Yazar profili detay + duzenleme."""
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    specialty_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    can_auto_publish = serializers.BooleanField(read_only=True)
    min_publish_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = DoctorAuthor
        fields = [
            'id', 'full_name', 'email',
            # Uzmanlik
            'primary_specialty', 'specialty_display',
            'secondary_specialties', 'sub_specialties',
            # Biyografi
            'bio_tr', 'bio_en', 'headline_tr', 'headline_en',
            # Akademik
            'education', 'publications', 'memberships',
            'orcid_id', 'google_scholar_url', 'pubmed_author_id',
            # Kurum
            'institution', 'department', 'city',
            # Yazar seviyesi
            'author_level', 'level_display',
            'total_articles', 'total_views', 'average_rating',
            'can_auto_publish', 'min_publish_score',
            # Dogrulama
            'is_verified', 'verified_at', 'verification_document',
            'profile_photo',
            # Sosyal
            'linkedin_url', 'website_url',
            # Durum
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'full_name', 'email',
            'author_level', 'level_display',
            'total_articles', 'total_views', 'average_rating',
            'can_auto_publish', 'min_publish_score',
            'is_verified', 'verified_at',
            'created_at', 'updated_at',
        ]

    def get_full_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_email(self, obj):
        return obj.doctor.user.email

    def get_specialty_display(self, obj):
        return obj.get_primary_specialty_display()

    def get_level_display(self, obj):
        return obj.get_author_level_display()


class DoctorAuthorCreateSerializer(serializers.ModelSerializer):
    """Yeni yazar profili olusturma. DoctorProfile'dan otomatik baglama."""

    class Meta:
        model = DoctorAuthor
        fields = [
            'primary_specialty', 'secondary_specialties', 'sub_specialties',
            'bio_tr', 'bio_en', 'headline_tr', 'headline_en',
            'education', 'publications', 'memberships',
            'orcid_id', 'google_scholar_url', 'pubmed_author_id',
            'institution', 'department', 'city',
            'profile_photo', 'linkedin_url', 'website_url',
        ]

    def validate(self, data):
        user = self.context['request'].user
        try:
            doctor_profile = user.doctor_profile
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError(
                'Yazar profili olusturmak icin doktor profili gereklidir.'
            )
        if hasattr(doctor_profile, 'author_profile'):
            raise serializers.ValidationError(
                'Bu doktorun zaten bir yazar profili var.'
            )
        data['_doctor_profile'] = doctor_profile
        return data

    def create(self, validated_data):
        doctor_profile = validated_data.pop('_doctor_profile')
        return DoctorAuthor.objects.create(
            doctor=doctor_profile,
            **validated_data,
        )


# ─────────────────────────────────────────────
# 2. Article (Blog/Egitim) Yonetim Serializer'lari
# ─────────────────────────────────────────────

class AuthorArticleListSerializer(serializers.ModelSerializer):
    """Yazarin makale listesi."""
    category_name = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title_tr', 'title_en',
            'excerpt_tr', 'status', 'is_featured',
            'category', 'category_name',
            'published_at', 'created_at', 'updated_at',
            'review_count',
        ]

    def get_category_name(self, obj):
        return obj.category.name_tr if obj.category else None

    def get_review_count(self, obj):
        return obj.reviews.count()


class AuthorArticleDetailSerializer(serializers.ModelSerializer):
    """Yazarin makale detayi + duzenleme."""
    category_name = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'body_tr', 'body_en',
            'featured_image', 'category', 'category_name',
            'status', 'is_featured', 'published_at',
            'seo_title_tr', 'seo_title_en',
            'seo_description_tr', 'seo_description_en',
            'created_at', 'updated_at',
            'reviews',
        ]
        read_only_fields = [
            'id', 'slug', 'status', 'is_featured',
            'published_at', 'created_at', 'updated_at',
        ]

    def get_category_name(self, obj):
        return obj.category.name_tr if obj.category else None

    def get_reviews(self, obj):
        return ArticleReviewSerializer(
            obj.reviews.order_by('-created_at')[:5],
            many=True,
        ).data


class AuthorArticleCreateSerializer(serializers.ModelSerializer):
    """Yazar yeni makale olusturma."""

    class Meta:
        model = Article
        fields = [
            'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'body_tr', 'body_en',
            'featured_image', 'category',
            'seo_title_tr', 'seo_title_en',
            'seo_description_tr', 'seo_description_en',
        ]

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid

        title = validated_data.get('title_tr', '')
        slug_base = slugify(title[:80]) or f'makale-{uuid.uuid4().hex[:8]}'
        slug = slug_base
        counter = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f'{slug_base}-{counter}'
            counter += 1

        validated_data['slug'] = slug
        validated_data['author'] = self.context['request'].user
        validated_data['status'] = 'draft'
        try:
            doctor_author = self.context['request'].user.doctor_profile.author_profile
            validated_data['doctor_author'] = doctor_author
        except Exception:
            pass
        return super().create(validated_data)


# ─────────────────────────────────────────────
# 3. NewsArticle Yonetim Serializer'lari
# ─────────────────────────────────────────────

class AuthorNewsListSerializer(serializers.ModelSerializer):
    """Yazarin haber listesi."""
    category_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'slug', 'title_tr',
            'category', 'category_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'is_auto_generated', 'view_count',
            'published_at', 'created_at',
            'review_count',
        ]

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_priority_display(self, obj):
        return obj.get_priority_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_review_count(self, obj):
        return obj.reviews.count()


class AuthorNewsDetailSerializer(serializers.ModelSerializer):
    """Yazarin haber detayi + duzenleme."""
    category_display = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'slug', 'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'body_tr', 'body_en',
            'category', 'category_display',
            'priority', 'status',
            'source_urls', 'original_source',
            'meta_title', 'meta_description',
            'keywords', 'schema_markup',
            'featured_image', 'featured_image_alt',
            'is_auto_generated', 'view_count',
            'published_at', 'created_at', 'updated_at',
            'reviews',
        ]
        read_only_fields = [
            'id', 'slug', 'status',
            'is_auto_generated', 'view_count',
            'published_at', 'created_at', 'updated_at',
        ]

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_reviews(self, obj):
        return ArticleReviewSerializer(
            obj.reviews.order_by('-created_at')[:5],
            many=True,
        ).data


class AuthorNewsCreateSerializer(serializers.ModelSerializer):
    """Yazar yeni haber olusturma."""

    class Meta:
        model = NewsArticle
        fields = [
            'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'body_tr', 'body_en',
            'category', 'priority',
            'source_urls', 'original_source',
            'meta_title', 'meta_description',
            'keywords',
            'featured_image', 'featured_image_alt',
        ]

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid

        title = validated_data.get('title_tr', '')
        slug_base = slugify(title[:80]) or f'haber-{uuid.uuid4().hex[:8]}'
        slug = slug_base
        counter = 1
        while NewsArticle.objects.filter(slug=slug).exists():
            slug = f'{slug_base}-{counter}'
            counter += 1

        validated_data['slug'] = slug
        validated_data['status'] = 'draft'

        # DoctorAuthor bagla
        user = self.context['request'].user
        try:
            author = user.doctor_profile.author_profile
            validated_data['author'] = author
        except Exception:
            pass

        return super().create(validated_data)


# ─────────────────────────────────────────────
# 4. ArticleReview Serializer
# ─────────────────────────────────────────────

class ArticleReviewSerializer(serializers.ModelSerializer):
    """Degerlendirme goruntuleme."""
    review_type_display = serializers.SerializerMethodField()
    decision_display = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = ArticleReview
        fields = [
            'id', 'review_type', 'review_type_display',
            'reviewer_name',
            'medical_accuracy_score', 'language_quality_score',
            'seo_score', 'style_compliance_score',
            'ethics_score', 'overall_score',
            'decision', 'decision_display',
            'feedback', 'created_at',
        ]

    def get_review_type_display(self, obj):
        return obj.get_review_type_display()

    def get_decision_display(self, obj):
        return obj.get_decision_display()

    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.get_full_name()
        return 'Sistem (Ajan)'


# ─────────────────────────────────────────────
# 5. Status Transition Serializer'lari
# ─────────────────────────────────────────────

class ArticleStatusTransitionSerializer(serializers.Serializer):
    """Makale durum gecisi."""
    action = serializers.ChoiceField(
        choices=['submit_for_review', 'approve', 'reject', 'publish', 'archive', 'revert_to_draft'],
    )
    feedback = serializers.CharField(required=False, allow_blank=True, default='')

    # Gecerli gecisler: {mevcut_durum: [izin_verilen_aksiyonlar]}
    ARTICLE_TRANSITIONS = {
        'draft': ['submit_for_review'],
        'published': ['archive'],
        'archived': ['revert_to_draft'],
    }

    # NewsArticle daha detayli akisa sahip
    NEWS_TRANSITIONS = {
        'draft': ['submit_for_review'],
        'review': ['approve', 'reject'],
        'revision': ['submit_for_review'],
        'approved': ['publish'],
        'published': ['archive'],
        'archived': ['revert_to_draft'],
    }


class NewsStatusTransitionSerializer(serializers.Serializer):
    """Haber durum gecisi."""
    action = serializers.ChoiceField(
        choices=['submit_for_review', 'approve', 'reject', 'publish', 'archive', 'revert_to_draft'],
    )
    feedback = serializers.CharField(required=False, allow_blank=True, default='')
