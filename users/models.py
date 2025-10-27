from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom user model with additional fields for the wiki community."""
    
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True, blank=True)
    
    # Profile fields
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Social fields
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    
    # Activity tracking
    last_active = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_display_name(self):
        """Return display name (username or email prefix)."""
        return self.username or self.email.split('@')[0]


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Statistics
    articles_created = models.PositiveIntegerField(default=0)
    articles_edited = models.PositiveIntegerField(default=0)
    posts_created = models.PositiveIntegerField(default=0)
    comments_created = models.PositiveIntegerField(default=0)
    
    # Achievements
    reputation = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    
    # Preferences
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ])
    
    language = models.CharField(max_length=10, default='zh-hans', choices=[
        ('zh-hans', '简体中文'),
        ('en', 'English'),
    ])
    
    def __str__(self):
        return f"{self.user.email} Profile"


class Follow(models.Model):
    """User following relationship."""
    
    follower = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='following'
    )
    followed = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['followed', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower} follows {self.followed}"