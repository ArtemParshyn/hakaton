from django.contrib import admin
from django.utils.html import format_html

from .models import ApiUser, NewsItem, Tag, UserNewSubscription

admin.site.register(UserNewSubscription)


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'is_organization_news', 'approve_button')
    list_filter = ('status', 'is_organization_news', 'tags', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    actions = ['approve_articles', 'archive_articles']
    readonly_fields = ('created_at',)
    filter_horizontal = ('tags',)

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'content', 'author', 'tags')
        }),
        ('Статус', {
            'fields': ('status', 'is_organization_news')
        }),
        ('Медиа', {
            'fields': ('cover', 'sources'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def approve_button(self, obj):
        if obj.status != 'PUBLISHED':
            return format_html(
                '<a class="button" href="/admin/api/newsitem/{}/change/?approve=1">Одобрить</a>',
                obj.id
            )
        return "Опубликовано"

    approve_button.short_description = "Действия"
    approve_button.allow_tags = True

    def approve_articles(self, request, queryset):
        queryset.update(status='PUBLISHED')

    approve_articles.short_description = "Одобрить выбранные статьи"

    def archive_articles(self, request, queryset):
        queryset.update(status='ARCHIVED')

    archive_articles.short_description = "Архивировать выбранные статьи"

    def save_model(self, request, obj, form, change):
        if 'approve' in request.GET:
            obj.status = 'PUBLISHED'
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'news_count')
    search_fields = ('name',)

    def news_count(self, obj):
        return obj.news_items.count()

    news_count.short_description = 'Количество статей'


@admin.register(ApiUser)
class ApiUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'authored_news_count')
    search_fields = ('username',)

    def authored_news_count(self, obj):
        return obj.authored_news.count()

    authored_news_count.short_description = 'Статей написано'

# Register your models here.
