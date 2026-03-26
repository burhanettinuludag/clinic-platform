from django.contrib import admin
from .models import (
    SleepCategory, SleepArticle, SleepTip, SleepFAQ,
    SleepScreeningTest, SleepScreeningQuestion,
    SleepScreeningOption, SleepScreeningResultRange,
)


@admin.register(SleepCategory)
class SleepCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_tr', 'name_en', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(SleepArticle)
class SleepArticleAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'category', 'article_type', 'related_disease',
                    'is_featured', 'is_published', 'view_count', 'order')
    list_filter = ('article_type', 'category', 'is_featured', 'is_published', 'related_disease')
    list_editable = ('is_featured', 'is_published', 'order')
    search_fields = ('title_tr', 'title_en', 'content_tr')
    prepopulated_fields = {'slug': ('title_en',)}
    readonly_fields = ('view_count',)


@admin.register(SleepTip)
class SleepTipAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'is_active', 'order')
    list_editable = ('is_active', 'order')


@admin.register(SleepFAQ)
class SleepFAQAdmin(admin.ModelAdmin):
    list_display = ('question_tr', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active', 'order')


# ── Screening Test Admin ───────────────────────────────────────────────

class SleepScreeningOptionInline(admin.TabularInline):
    model = SleepScreeningOption
    extra = 1
    fields = ('text_tr', 'text_en', 'score', 'order')


class SleepScreeningQuestionInline(admin.TabularInline):
    model = SleepScreeningQuestion
    extra = 1
    fields = ('question_tr', 'question_en', 'order')
    show_change_link = True


class SleepScreeningResultRangeInline(admin.TabularInline):
    model = SleepScreeningResultRange
    extra = 1
    fields = ('level', 'min_score', 'max_score', 'title_tr', 'title_en', 'color')


@admin.register(SleepScreeningTest)
class SleepScreeningTestAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'slug', 'duration_minutes', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [SleepScreeningQuestionInline, SleepScreeningResultRangeInline]


@admin.register(SleepScreeningQuestion)
class SleepScreeningQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_tr', 'test', 'order')
    list_filter = ('test',)
    inlines = [SleepScreeningOptionInline]
