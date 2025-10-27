from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PostCategory, Post, PostLike, PostComment, CommentLike, 
    PostShare, PostReport, PostTag
)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_display', 'post_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ['author', 'content', 'created_at']
    can_delete = False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status', 'post_type', 
        'is_pinned', 'is_featured', 'views_count', 'likes_count', 
        'comments_count', 'created_at'
    ]
    list_filter = ['status', 'post_type', 'is_pinned', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['views_count', 'likes_count', 'comments_count', 'shares_count']
    list_editable = ['status', 'is_pinned', 'is_featured']
    date_hierarchy = 'created_at'
    inlines = [PostCommentInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'content', 'author', 'category']
        }),
        ('Status and Type', {
            'fields': ['status', 'post_type', 'is_pinned', 'is_featured', 'is_approved']
        }),
        ('Statistics', {
            'fields': ['views_count', 'likes_count', 'comments_count', 'shares_count'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'published_at', 'closed_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'user__username']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'user')


class CommentLikeInline(admin.TabularInline):
    model = CommentLike
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = [
        'content_preview', 'post', 'author', 'parent', 'is_approved', 
        'likes_count', 'reported_count', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'post__title', 'author__username']
    list_editable = ['is_approved']
    readonly_fields = ['likes_count', 'reported_count']
    date_hierarchy = 'created_at'
    inlines = [CommentLikeInline]
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'author', 'parent')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment__content', 'user__username']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comment', 'user')


@admin.register(PostShare)
class PostShareAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'shared_to', 'created_at']
    list_filter = ['shared_to', 'created_at']
    search_fields = ['post__title', 'user__username', 'message']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'user')


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = [
        'target_display', 'reporter', 'report_type', 'status', 'created_at'
    ]
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['reporter__username', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Report Details', {
            'fields': ['reporter', 'post', 'comment', 'report_type', 'description']
        }),
        ('Moderation', {
            'fields': ['status', 'moderator_notes']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at']
        }),
    ]
    
    def target_display(self, obj):
        if obj.post:
            return f"Post: {obj.post.title}"
        elif obj.comment:
            return f"Comment: {obj.comment.content[:30]}..."
        return "Unknown"
    target_display.short_description = 'Target'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reporter', 'post', 'comment')


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}