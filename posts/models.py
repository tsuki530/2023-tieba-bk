from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

User = get_user_model()

class PostCategory(models.Model):
    """Category for organizing posts."""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('post category')
        verbose_name_plural = _('post categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """Post model for community discussions."""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('closed', _('Closed')),
        ('archived', _('Archived')),
    ]
    
    TYPE_CHOICES = [
        ('discussion', _('Discussion')),
        ('question', _('Question')),
        ('announcement', _('Announcement')),
        ('news', _('News')),
    ]
    
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name='posts')
    
    # Status and type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    post_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='discussion')
    
    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['is_pinned', 'created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        # Set closed_at when status changes to closed
        if self.status == 'closed' and not self.closed_at:
            from django.utils import timezone
            self.closed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    def increment_views(self):
        """Increment view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class PostLike(models.Model):
    """Like relationship for posts."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} likes {self.post}"


class PostComment(models.Model):
    """Comment model for posts."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='replies')
    
    content = models.TextField(max_length=2000)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    reported_count = models.PositiveIntegerField(default=0)
    
    # Statistics
    likes_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('post comment')
        verbose_name_plural = _('post comments')
        ordering = ['created_at']  # Chronological order for comments
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
    
    def is_reply(self):
        """Check if this comment is a reply."""
        return self.parent is not None


class CommentLike(models.Model):
    """Like relationship for post comments."""
    
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user} likes comment {self.comment.id}"


class PostShare(models.Model):
    """Share relationship for posts."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_to = models.CharField(max_length=50, choices=[
        ('timeline', 'Timeline'),
        ('message', 'Message'),
        ('external', 'External'),
    ])
    message = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} shared {self.post}"


class PostReport(models.Model):
    """Report model for posts and comments."""
    
    REPORT_TYPES = [
        ('spam', _('Spam')),
        ('harassment', _('Harassment')),
        ('hate_speech', _('Hate Speech')),
        ('misinformation', _('Misinformation')),
        ('inappropriate', _('Inappropriate Content')),
        ('other', _('Other')),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Target can be either a post or a comment
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(max_length=1000, blank=True)
    
    # Moderation status
    status = models.CharField(max_length=20, choices=[
        ('pending', _('Pending')),
        ('reviewed', _('Reviewed')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
    ], default='pending')
    
    moderator_notes = models.TextField(blank=True, max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('post report')
        verbose_name_plural = _('post reports')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        target = self.post or self.comment
        return f"Report on {target} by {self.reporter}"
    
    def clean(self):
        """Ensure either post or comment is set, but not both."""
        from django.core.exceptions import ValidationError
        if not self.post and not self.comment:
            raise ValidationError('Either post or comment must be set.')
        if self.post and self.comment:
            raise ValidationError('Cannot set both post and comment.')


class PostTag(models.Model):
    """Tag for posts."""
    
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('post tag')
        verbose_name_plural = _('post tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name