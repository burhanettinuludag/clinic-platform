from django.contrib import admin
from .models import ContentCategory, Article, EducationItem, EducationProgress


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'slug', 'parent', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name_en',)}
    search_fields = ('name_tr', 'name_en')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'category', 'author', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'is_featured', 'category', 'published_at')
    list_editable = ('status', 'is_featured')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('title_tr', 'title_en')
    date_hierarchy = 'published_at'


@admin.register(EducationItem)
class EducationItemAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'disease_module', 'content_type', 'order', 'is_published')
    list_filter = ('content_type', 'disease_module', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('title_tr', 'title_en')


@admin.register(EducationProgress)
class EducationProgressAdmin(admin.ModelAdmin):
    list_display = ('patient', 'education_item', 'progress_percent', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('patient__email',)


from apps.content.models import NewsArticle, ArticleReview

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title_tr', 'category', 'priority', 'status', 'is_auto_generated', 'published_at']
    list_filter = ['category', 'priority', 'status', 'is_auto_generated']
    search_fields = ['title_tr', 'title_en']
    prepopulated_fields = {'slug': ('title_tr',)}

@admin.register(ArticleReview)
class ArticleReviewAdmin(admin.ModelAdmin):
    list_display = ['review_type', 'overall_score', 'decision', 'created_at']
    list_filter = ['review_type', 'decision']
