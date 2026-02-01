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

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'excerpt', 'body', 'featured_image',
            'category', 'category_name', 'author_name',
            'is_featured', 'published_at',
            'seo_title', 'seo_description',
        ]

    def get_body(self, obj):
        return getattr(obj, f'body_{self._get_lang()}', obj.body_tr)

    def get_seo_title(self, obj):
        return getattr(obj, f'seo_title_{self._get_lang()}', obj.seo_title_tr)

    def get_seo_description(self, obj):
        return getattr(obj, f'seo_description_{self._get_lang()}', obj.seo_description_tr)


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
