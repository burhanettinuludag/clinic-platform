from rest_framework import serializers
from .models import ContentCategory, Article, EducationItem, EducationProgress


class ContentCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = ContentCategory
        fields = ['id', 'slug', 'name', 'name_tr', 'name_en', 'parent', 'order', 'children']

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_children(self, obj):
        children = obj.children.all()
        if children.exists():
            return ContentCategorySerializer(children, many=True, context=self.context).data
        return []


class ArticleListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'excerpt', 'featured_image',
            'category', 'category_name', 'author_name',
            'is_featured', 'published_at',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_excerpt(self, obj):
        return getattr(obj, f'excerpt_{self._get_lang()}', obj.excerpt_tr)

    def get_category_name(self, obj):
        if obj.category:
            return getattr(obj.category, f'name_{self._get_lang()}', obj.category.name_tr)
        return None

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None


class ArticleDetailSerializer(ArticleListSerializer):
    body = serializers.SerializerMethodField()
    seo_title = serializers.SerializerMethodField()
    seo_description = serializers.SerializerMethodField()
    schema_markup = serializers.SerializerMethodField()
    author_profile = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'excerpt', 'body', 'featured_image',
            'category', 'category_name', 'author_name', 'author_profile',
            'is_featured', 'published_at',
            'seo_title', 'seo_description', 'schema_markup',
        ]

    def get_body(self, obj):
        return getattr(obj, f'body_{self._get_lang()}', obj.body_tr)

    def get_seo_title(self, obj):
        return getattr(obj, f'seo_title_{self._get_lang()}', obj.seo_title_tr)

    def get_seo_description(self, obj):
        return getattr(obj, f'seo_description_{self._get_lang()}', obj.seo_description_tr)

    def get_schema_markup(self, obj):
        from apps.content.schema_markup import generate_article_schema
        request = self.context.get('request')
        try:
            return generate_article_schema(obj, request)
        except Exception:
            return {}

    def get_author_profile(self, obj):
        if not obj.author:
            return None
        try:
            da = obj.author.doctor_profile.author_profile
            return {
                'specialty': da.get_primary_specialty_display(),
                'institution': da.institution,
                'department': da.department,
                'bio': da.bio_tr[:200] if da.bio_tr else '',
                'is_verified': da.is_verified,
                'author_level': da.author_level,
                'orcid_id': da.orcid_id,
                'profile_photo': da.profile_photo.url if da.profile_photo else None,
            }
        except Exception:
            return None


class EducationItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    disease_module_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = EducationItem
        fields = [
            'id', 'slug', 'title', 'body', 'content_type', 'video_url',
            'image', 'disease_module', 'disease_module_slug', 'category', 'category_name', 'order',
            'estimated_duration_minutes', 'progress',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_body(self, obj):
        return getattr(obj, f'body_{self._get_lang()}', obj.body_tr)

    def get_disease_module_slug(self, obj):
        if obj.disease_module:
            return obj.disease_module.slug
        return None

    def get_category_name(self, obj):
        if obj.category:
            return getattr(obj.category, f'name_{self._get_lang()}', obj.category.name_tr)
        return None

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            prog = obj.progress_records.filter(patient=request.user).first()
            if prog:
                return {
                    'id': str(prog.id),
                    'progress_percent': prog.progress_percent,
                    'completed_at': prog.completed_at,
                }
        return None


class EducationProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationProgress
        fields = ['id', 'education_item', 'progress_percent', 'started_at', 'completed_at']
        read_only_fields = ['started_at']


# ─────────────────────────────────────────────
# NewsArticle Public Serializers
# ─────────────────────────────────────────────

class NewsArticleListSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'slug', 'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'category', 'category_display',
            'priority', 'priority_display',
            'featured_image', 'featured_image_alt',
            'author_name', 'published_at', 'view_count',
        ]

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_priority_display(self, obj):
        return obj.get_priority_display()

    def get_author_name(self, obj):
        if obj.author:
            try:
                return obj.author.doctor.user.get_full_name()
            except Exception:
                pass
        return None


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_profile = serializers.SerializerMethodField()
    schema_markup = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'slug', 'title_tr', 'title_en',
            'excerpt_tr', 'excerpt_en',
            'body_tr', 'body_en',
            'category', 'category_display',
            'priority', 'source_urls', 'original_source',
            'meta_title', 'meta_description', 'keywords',
            'featured_image', 'featured_image_alt',
            'author_name', 'author_profile', 'schema_markup',
            'published_at', 'updated_at', 'view_count',
        ]

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_author_name(self, obj):
        if obj.author:
            try:
                return obj.author.doctor.user.get_full_name()
            except Exception:
                pass
        return None

    def get_author_profile(self, obj):
        if not obj.author:
            return None
        da = obj.author
        return {
            'specialty': da.get_primary_specialty_display(),
            'institution': da.institution,
            'department': da.department,
            'bio': da.bio_tr[:200] if da.bio_tr else '',
            'is_verified': da.is_verified,
            'orcid_id': da.orcid_id,
            'profile_photo': da.profile_photo.url if da.profile_photo else None,
        }

    def get_schema_markup(self, obj):
        try:
            from apps.content.schema_markup import build_news_article_schema
            return build_news_article_schema(obj)
        except Exception:
            return None

# --- Public Doctor Profile ---

class PublicDoctorAuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    specialty_display = serializers.CharField(source='get_primary_specialty_display', read_only=True)
    slug = serializers.SerializerMethodField()
    article_count = serializers.IntegerField(source='total_articles', read_only=True)
    schema_markup = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAuthor
        fields = [
            'id', 'full_name', 'slug', 'primary_specialty', 'specialty_display',
            'headline_tr', 'headline_en', 'bio_tr', 'bio_en',
            'institution', 'department', 'city',
            'profile_photo', 'orcid_id', 'google_scholar_url',
            'linkedin_url', 'website_url', 'is_verified',
            'article_count', 'total_views', 'average_rating',
            'memberships', 'education', 'schema_markup',
        ]

    def get_full_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_slug(self, obj):
        name = obj.doctor.user.get_full_name().lower().replace(' ', '-')
        import re
        name = re.sub(r'[^a-z0-9-]', '', name)
        return f"{name}-{str(obj.id)[:8]}"

    def get_schema_markup(self, obj):
        return {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": obj.doctor.user.get_full_name(),
            "jobTitle": obj.get_primary_specialty_display(),
            "affiliation": {"@type": "Organization", "name": obj.institution} if obj.institution else None,
            "description": obj.bio_tr,
            "image": obj.profile_photo.url if obj.profile_photo else None,
            "sameAs": [u for u in [obj.orcid_id and f"https://orcid.org/{obj.orcid_id}", obj.google_scholar_url, obj.linkedin_url, obj.website_url] if u],
        }
