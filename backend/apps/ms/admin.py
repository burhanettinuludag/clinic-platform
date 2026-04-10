from django.contrib import admin
from .models import MSCategory, MSArticle, MSTip, MSFAQ


@admin.register(MSCategory)
class MSCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(MSArticle)
class MSArticleAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'category', 'article_type',
                    'is_featured', 'is_published', 'view_count', 'order')
    list_filter = ('article_type', 'category', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published', 'order')
    search_fields = ('title_tr', 'title_en', 'content_tr')
    prepopulated_fields = {'slug': ('title_en',)}
    readonly_fields = ('view_count',)


@admin.register(MSTip)
class MSTipAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'is_active', 'order')
    list_editable = ('is_active', 'order')


@admin.register(MSFAQ)
class MSFAQAdmin(admin.ModelAdmin):
    list_display = ('question_tr', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active', 'order')
