from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    PostCategory, Post, PostLike, PostComment, CommentLike, 
    PostShare, PostReport, PostTag
)

User = get_user_model()


class PostCategorySerializer(serializers.ModelSerializer):
    """Serializer for post categories."""
    
    post_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PostCategory
        fields = ['id', 'name', 'slug', 'description', 'color', 
                 'post_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simplified user serializer for nested representations."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']


class PostTagSerializer(serializers.ModelSerializer):
    """Serializer for post tags."""
    
    class Meta:
        model = PostTag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view (optimized for listing)."""
    
    author = UserSimpleSerializer(read_only=True)
    category = PostCategorySerializer(read_only=True)
    excerpt = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'excerpt', 'author', 'category', 'status', 
            'post_type', 'is_pinned', 'is_featured', 'views_count', 
            'likes_count', 'comments_count', 'created_at', 'published_at'
        ]
        read_only_fields = ['id', 'created_at', 'published_at']
    
    def get_excerpt(self, obj):
        """Generate excerpt from content."""
        return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for post detail view."""
    
    author = UserSimpleSerializer(read_only=True)
    category = PostCategorySerializer(read_only=True)
    tags = PostTagSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'category', 'tags',
            'status', 'post_type', 'is_pinned', 'is_featured', 'is_approved',
            'views_count', 'likes_count', 'comments_count', 'shares_count',
            'is_liked', 'created_at', 'updated_at', 'published_at', 'closed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'closed_at']
    
    def get_is_liked(self, obj):
        """Check if current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'post_type', 'status']
    
    def create(self, validated_data):
        """Set the author to the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'post_type', 'status']


class PostCommentSerializer(serializers.ModelSerializer):
    """Serializer for post comments."""
    
    author = UserSimpleSerializer(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = [
            'id', 'post', 'author', 'parent', 'content', 'is_approved',
            'replies_count', 'likes_count', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        """Check if current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating post comments."""
    
    class Meta:
        model = PostComment
        fields = ['post', 'parent', 'content']
    
    def create(self, validated_data):
        """Set the author to the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for post likes."""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializer for comment likes."""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'comment', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostShareSerializer(serializers.ModelSerializer):
    """Serializer for post shares."""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostShare
        fields = ['id', 'post', 'user', 'shared_to', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostShareCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating post shares."""
    
    class Meta:
        model = PostShare
        fields = ['post', 'shared_to', 'message']
    
    def create(self, validated_data):
        """Set the user to the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class PostReportSerializer(serializers.ModelSerializer):
    """Serializer for post reports."""
    
    reporter = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostReport
        fields = [
            'id', 'reporter', 'post', 'comment', 'report_type', 
            'description', 'status', 'moderator_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PostReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating post reports."""
    
    class Meta:
        model = PostReport
        fields = ['post', 'comment', 'report_type', 'description']
    
    def validate(self, data):
        """Validate that either post or comment is provided, but not both."""
        if not data.get('post') and not data.get('comment'):
            raise serializers.ValidationError("Either post or comment must be provided.")
        if data.get('post') and data.get('comment'):
            raise serializers.ValidationError("Cannot provide both post and comment.")
        return data
    
    def create(self, validated_data):
        """Set the reporter to the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['reporter'] = request.user
        return super().create(validated_data)


class PostStatsSerializer(serializers.Serializer):
    """Serializer for post statistics."""
    
    total_posts = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_views = serializers.IntegerField()
    popular_posts = PostListSerializer(many=True)
    recent_posts = PostListSerializer(many=True)