from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Tag, Article, ArticleVersion, ArticleLike, 
    ArticleComment, ArticleBookmark, CommentLike
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_display', 'article_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


class ArticleVersionInline(admin.TabularInline):
    model = ArticleVersion
    extra = 0
    readonly_fields = ['author', 'title', 'content', 'created_at']
    can_delete = False


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    readonly_fields = ['author', 'content', 'created_at']
    can_delete = False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'slug', 'author', 'category', 'status', 
        'featured', 'views_count', 'likes_count', 
        'comments_count', 'created_at'
    ]
    list_filter = ['status', 'featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['views_count', 'likes_count', 'comments_count']
    list_editable = ['status', 'featured']
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleVersionInline, ArticleCommentInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'slug', 'content', 'author', 'category', 'tags']
        }),
        ('Status and Features', {
            'fields': ['status', 'featured']
        }),
        ('Statistics', {
            'fields': ['views_count', 'likes_count', 'comments_count'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'published_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ['article', 'title_preview', 'author', 'change_description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'author__username', 'change_description']
    readonly_fields = ['article', 'author', 'title', 'content', 'change_description', 'created_at']
    date_hierarchy = 'created_at'
    
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_preview.short_description = 'Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'author')


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__username']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'user')


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = [
        'content_preview', 'article', 'author', 'parent', 'is_approved', 
        'likes_count', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'article__title', 'author__username']
    list_editable = ['is_approved']
    readonly_fields = ['likes_count']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'author', 'parent')