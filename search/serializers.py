from rest_framework import serializers
from django.contrib.auth import get_user_model
from wiki.models import Article, Category, Tag
from posts.models import Post, PostCategory

User = get_user_model()


class SearchResultSerializer(serializers.Serializer):
    """Serializer for unified search results."""
    
    id = serializers.CharField()
    title = serializers.CharField()
    content = serializers.CharField()
    type = serializers.CharField()  # 'article', 'post', 'user', etc.
    url = serializers.CharField()
    score = serializers.FloatField(required=False)
    
    # Additional fields based on type
    author = serializers.DictField(required=False)
    category = serializers.DictField(required=False)
    tags = serializers.ListField(required=False)
    created_at = serializers.DateTimeField(required=False)
    views_count = serializers.IntegerField(required=False)
    likes_count = serializers.IntegerField(required=False)


class ArticleSearchSerializer(serializers.ModelSerializer):
    """Serializer for article search results."""
    
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'type', 'url', 'author', 
            'category', 'tags', 'created_at', 'views_count', 'likes_count'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'slug': obj.category.slug
            }
        return None
    
    def get_tags(self, obj):
        return [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in obj.tags.all()]
    
    def get_url(self, obj):
        return f"/articles/{obj.slug}/"
    
    def get_type(self, obj):
        return 'article'


class PostSearchSerializer(serializers.ModelSerializer):
    """Serializer for post search results."""
    
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'type', 'url', 'author', 
            'category', 'created_at', 'views_count', 'likes_count', 'comments_count'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'slug': obj.category.slug
            }
        return None
    
    def get_url(self, obj):
        return f"/posts/{obj.id}/"
    
    def get_type(self, obj):
        return 'post'


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user search results."""
    
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'type', 'url']
    
    def get_url(self, obj):
        return f"/users/{obj.username}/"
    
    def get_type(self, obj):
        return 'user'


class CategorySearchSerializer(serializers.ModelSerializer):
    """Serializer for category search results."""
    
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'type', 'url']
    
    def get_url(self, obj):
        return f"/categories/{obj.slug}/"
    
    def get_type(self, obj):
        return 'category'


class TagSearchSerializer(serializers.ModelSerializer):
    """Serializer for tag search results."""
    
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'type', 'url']
    
    def get_url(self, obj):
        return f"/tags/{obj.slug}/"
    
    def get_type(self, obj):
        return 'tag'


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search query parameters."""
    
    q = serializers.CharField(required=True, max_length=200)
    type = serializers.ChoiceField(
        choices=['all', 'articles', 'posts', 'users', 'categories', 'tags'],
        default='all'
    )
    category = serializers.CharField(required=False, max_length=50)
    tag = serializers.CharField(required=False, max_length=50)
    author = serializers.CharField(required=False, max_length=50)
    sort_by = serializers.ChoiceField(
        choices=['relevance', 'date', 'views', 'likes'],
        default='relevance'
    )
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class SearchStatsSerializer(serializers.Serializer):
    """Serializer for search statistics."""
    
    total_results = serializers.IntegerField()
    articles_count = serializers.IntegerField()
    posts_count = serializers.IntegerField()
    users_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    tags_count = serializers.IntegerField()
    search_time = serializers.FloatField()
    query = serializers.CharField()


class AutocompleteResultSerializer(serializers.Serializer):
    """Serializer for autocomplete results."""
    
    id = serializers.CharField()
    text = serializers.CharField()
    type = serializers.CharField()
    url = serializers.CharField()
    score = serializers.FloatField(required=False)