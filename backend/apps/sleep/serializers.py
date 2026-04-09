from rest_framework import serializers
from .models import (
    SleepCategory, SleepArticle, SleepTip, SleepFAQ,
    SleepScreeningTest, SleepScreeningQuestion,
    SleepScreeningOption, SleepScreeningResultRange,
)


class _LangMixin:
    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'


class SleepCategorySerializer(_LangMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = SleepCategory
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


class SleepArticleListSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = SleepArticle
        fields = [
            'id', 'slug', 'article_type', 'title', 'subtitle', 'summary',
            'category_name', 'related_disease', 'cover_image', 'cover_image_url',
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


class SleepArticleDetailSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    meta_title = serializers.SerializerMethodField()
    meta_description = serializers.SerializerMethodField()
    category = SleepCategorySerializer(read_only=True)

    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = SleepArticle
        fields = [
            'id', 'slug', 'article_type', 'title', 'subtitle',
            'content', 'summary', 'category', 'related_disease',
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


class SleepTipSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = SleepTip
        fields = ['id', 'title', 'content', 'icon', 'order']

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_content(self, obj):
        return getattr(obj, f'content_{self._get_lang()}', obj.content_tr)


class SleepFAQSerializer(_LangMixin, serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = SleepFAQ
        fields = ['id', 'question', 'answer', 'order']

    def get_question(self, obj):
        return getattr(obj, f'question_{self._get_lang()}', obj.question_tr)

    def get_answer(self, obj):
        return getattr(obj, f'answer_{self._get_lang()}', obj.answer_tr)


# ── Screening Test Serializers ─────────────────────────────────────────

class SleepScreeningOptionSerializer(_LangMixin, serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = SleepScreeningOption
        fields = ['id', 'text', 'score', 'order']

    def get_text(self, obj):
        return getattr(obj, f'text_{self._get_lang()}', obj.text_tr)


class SleepScreeningQuestionSerializer(_LangMixin, serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    help_text = serializers.SerializerMethodField()
    options = SleepScreeningOptionSerializer(many=True, read_only=True)

    class Meta:
        model = SleepScreeningQuestion
        fields = ['id', 'question', 'help_text', 'order', 'options']

    def get_question(self, obj):
        return getattr(obj, f'question_{self._get_lang()}', obj.question_tr)

    def get_help_text(self, obj):
        return getattr(obj, f'help_text_{self._get_lang()}', obj.help_text_tr)


class SleepScreeningResultRangeSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    recommendation = serializers.SerializerMethodField()

    class Meta:
        model = SleepScreeningResultRange
        fields = [
            'id', 'level', 'min_score', 'max_score',
            'title', 'description', 'recommendation', 'color',
        ]

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)

    def get_recommendation(self, obj):
        return getattr(obj, f'recommendation_{self._get_lang()}', obj.recommendation_tr)


class SleepScreeningTestListSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = SleepScreeningTest
        fields = [
            'id', 'slug', 'title', 'description', 'icon',
            'duration_minutes', 'question_count', 'order',
        ]

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)

    def get_question_count(self, obj):
        return obj.questions.count()


class SleepScreeningTestDetailSerializer(_LangMixin, serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    instructions = serializers.SerializerMethodField()
    questions = SleepScreeningQuestionSerializer(many=True, read_only=True)
    result_ranges = SleepScreeningResultRangeSerializer(many=True, read_only=True)

    class Meta:
        model = SleepScreeningTest
        fields = [
            'id', 'slug', 'title', 'description', 'instructions',
            'icon', 'duration_minutes', 'order',
            'questions', 'result_ranges',
        ]

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)

    def get_instructions(self, obj):
        return getattr(obj, f'instructions_{self._get_lang()}', obj.instructions_tr)
