from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Tag, Article, ArticleVersion, ArticleLike, 
    ArticleComment, ArticleBookmark, CommentLike
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    article_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 
                 'article_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    
    article_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'article_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simplified user serializer for nested representations."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for article list view (optimized for listing)."""
    
    author = UserSimpleSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    excerpt = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category', 'tags',
            'status', 'views_count', 'likes_count', 'comments_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_excerpt(self, obj):
        """Generate excerpt from content."""
        return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for article detail view."""
    
    author = UserSimpleSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'category', 'tags',
            'status', 'featured', 'views_count', 
            'likes_count', 'comments_count', 'is_liked', 
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'published_at']
    
    def get_is_liked(self, obj):
        """Check if current user has liked this article."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating articles."""
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags', 'status']
    
    def create(self, validated_data):
        """Set the author and handle tags."""
        tags_data = validated_data.pop('tags', [])
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        
        article = super().create(validated_data)
        
        # Handle tags
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            article.tags.add(tag)
        
        return article


class ArticleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating articles."""
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags', 'status']
    
    def update(self, instance, validated_data):
        """Handle tags and create version history."""
        tags_data = validated_data.pop('tags', None)
        
        # Create version before updating
        ArticleVersion.objects.create(
            article=instance,
            title=instance.title,
            content=instance.content,
            editor=self.context['request'].user,
            version_notes=f"Updated via API"
        )
        
        article = super().update(instance, validated_data)
        
        # Update tags if provided
        if tags_data is not None:
            article.tags.clear()
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                article.tags.add(tag)
        
        return article


class ArticleVersionSerializer(serializers.ModelSerializer):
    """Serializer for article versions."""
    
    editor = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = ArticleVersion
        fields = [
            'id', 'article', 'title', 'content', 'editor', 
            'version_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ArticleLikeSerializer(serializers.ModelSerializer):
    """Serializer for article likes."""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = ArticleLike
        fields = ['id', 'article', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArticleCommentSerializer(serializers.ModelSerializer):
    """Serializer for article comments."""
    
    author = UserSimpleSerializer(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticleComment
        fields = [
            'id', 'article', 'author', 'parent', 'content', 'is_approved',
            'replies_count', 'likes_count', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        """Check if current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class ArticleCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating article comments."""
    
    class Meta:
        model = ArticleComment
        fields = ['article', 'parent', 'content']
    
    def create(self, validated_data):
        """Set the author to the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)





class ArticleStatsSerializer(serializers.Serializer):
    """Serializer for article statistics."""
    
    total_articles = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    popular_articles = ArticleListSerializer(many=True)
    recent_articles = ArticleListSerializer(many=True)
    featured_articles = ArticleListSerializer(many=True)