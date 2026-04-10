from rest_framework import serializers
from .models import MSCategory, MSArticle, MSTip, MSFAQ


class _LangMixin:
    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'


class MSCategorySerializer(_LangMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = MSCategory
        fields = [
            'id', 'slug', 'name', 'name_tr', 'name_en',
            'description', 'description_tr', 'description_en',
            'icon', 'order', 'article_count',
        ]

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)

    def get_article_count(self, obj):
        return obj.articles.filter(is_published=True).count()


class MSArticleListSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = MSArticle
        fields = [
            'id', 'slug', 'article_type', 'title', 'subtitle', 'summary',
            'category_name', 'cover_image', 'cover_image_url',
            'icon', 'reading_time_minutes', 'is_featured', 'view_count',
            'author_name', 'created_at',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return obj.cover_image_url or ''

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_subtitle(self, obj):
        return getattr(obj, f'subtitle_{self._get_lang()}', obj.subtitle_tr)

    def get_summary(self, obj):
        return getattr(obj, f'summary_{self._get_lang()}', obj.summary_tr)

    def get_category_name(self, obj):
        lang = self._get_lang()
        return getattr(obj.category, f'name_{lang}', obj.category.name_tr)


class MSArticleDetailSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    meta_title = serializers.SerializerMethodField()
    meta_description = serializers.SerializerMethodField()
    category = MSCategorySerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = MSArticle
        fields = [
            'id', 'slug', 'article_type', 'title', 'subtitle',
            'content', 'summary', 'category',
            'cover_image', 'cover_image_url', 'icon', 'reading_time_minutes',
            'is_featured', 'view_count', 'references',
            'author_name', 'meta_title', 'meta_description',
            'created_at', 'updated_at',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return obj.cover_image_url or ''

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_subtitle(self, obj):
        return getattr(obj, f'subtitle_{self._get_lang()}', obj.subtitle_tr)

    def get_content(self, obj):
        return getattr(obj, f'content_{self._get_lang()}', obj.content_tr)

    def get_summary(self, obj):
        return getattr(obj, f'summary_{self._get_lang()}', obj.summary_tr)

    def get_meta_title(self, obj):
        return getattr(obj, f'meta_title_{self._get_lang()}', obj.meta_title_tr)

    def get_meta_description(self, obj):
        return getattr(obj, f'meta_description_{self._get_lang()}', obj.meta_description_tr)


class MSTipSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = MSTip
        fields = ['id', 'title', 'content', 'icon', 'order']

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_content(self, obj):
        return getattr(obj, f'content_{self._get_lang()}', obj.content_tr)


class MSFAQSerializer(_LangMixin, serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = MSFAQ
        fields = ['id', 'question', 'answer', 'order']

    def get_question(self, obj):
        return getattr(obj, f'question_{self._get_lang()}', obj.question_tr)

    def get_answer(self, obj):
        return getattr(obj, f'answer_{self._get_lang()}', obj.answer_tr)
