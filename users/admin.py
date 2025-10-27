from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Follow

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom user admin configuration."""
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('avatar', 'bio', 'location', 'website')
        }),
        ('Social Information', {
            'fields': ('followers_count', 'following_count')
        }),
        ('Preferences', {
            'fields': ('email_notifications',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin configuration."""
    
    list_display = ('user', 'reputation', 'level', 'articles_created', 'articles_edited')
    list_filter = ('level', 'theme', 'language')
    search_fields = ('user__email', 'user__username')
    raw_id_fields = ('user',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Follow relationship admin configuration."""
    
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__email', 'followed__email')
    raw_id_fields = ('follower', 'followed')