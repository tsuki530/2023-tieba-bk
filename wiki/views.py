from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Category, Tag, Article, ArticleVersion, ArticleLike, 
    ArticleComment, ArticleBookmark, CommentLike
)
from .serializers import *

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination for consistent results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for categories."""
    
    queryset = Category.objects.annotate(
        article_count=Count('articles', distinct=True)
    ).order_by('name')
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tags (read-only)."""
    
    queryset = Tag.objects.annotate(
        article_count=Count('articles', distinct=True)
    ).order_by('name')
    serializer_class = TagSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by search term."""
        queryset = self.queryset
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for articles."""
    
    queryset = Article.objects.select_related('author', 'category').prefetch_related('tags')
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        elif self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = self.queryset.filter(status='published')
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Filter by author
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Search by title and content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Order by featured first, then by creation date
        queryset = queryset.order_by('-is_featured', '-created_at')
        
        return queryset.distinct()
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        """Record view when retrieving article."""
        instance = self.get_object()
        
        # Update view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Set author and handle published_at."""
        article = serializer.save(author=self.request.user)
        if article.status == 'published' and not article.published_at:
            article.published_at = timezone.now()
            article.save()
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        """Like or unlike an article."""
        article = self.get_object()
        like, created = ArticleLike.objects.get_or_create(
            article=article, 
            user=request.user
        )
        
        if not created:
            # Unlike if already liked
            like.delete()
            article.likes_count = max(0, article.likes_count - 1)
            message = 'Article unliked'
        else:
            article.likes_count += 1
            message = 'Article liked'
        
        article.save(update_fields=['likes_count'])
        return Response({'message': message, 'likes_count': article.likes_count})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, slug=None):
        """Rate an article."""
        # Rating functionality is not implemented yet
        return Response(
            {'error': 'Rating functionality is not implemented yet.'}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    @action(detail=True, methods=['get'])
    def versions(self, request, slug=None):
        """Get article version history."""
        article = self.get_object()
        versions = ArticleVersion.objects.filter(article=article).order_by('-created_at')
        serializer = ArticleVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured articles."""
        featured_articles = self.get_queryset().filter(
            is_featured=True, 
            status='published'
        )[:10]
        serializer = self.get_serializer(featured_articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular articles (by views)."""
        popular_articles = self.get_queryset().order_by('-views_count')[:10]
        serializer = self.get_serializer(popular_articles, many=True)
        return Response(serializer.data)


class ArticleVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for article versions (read-only)."""
    
    queryset = ArticleVersion.objects.select_related('article', 'editor')
    serializer_class = ArticleVersionSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by article."""
        queryset = self.queryset
        
        article_slug = self.request.query_params.get('article')
        if article_slug:
            queryset = queryset.filter(article__slug=article_slug)
        
        return queryset.order_by('-created_at')


class ArticleCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for article comments."""
    
    queryset = ArticleComment.objects.select_related('author', 'article', 'parent')
    serializer_class = ArticleCommentSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ArticleCommentCreateSerializer
        return ArticleCommentSerializer
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = self.queryset.filter(is_approved=True)
        
        # Filter by article
        article_slug = self.request.query_params.get('article')
        if article_slug:
            queryset = queryset.filter(article__slug=article_slug)
        
        # Filter by parent (for replies)
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            # Only top-level comments by default
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.order_by('created_at')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Set author and update article comment count."""
        comment = serializer.save(author=self.request.user)
        
        # Update article comment count
        article = comment.article
        article.comments_count += 1
        article.save(update_fields=['comments_count'])
    
    def perform_destroy(self, instance):
        """Update article comment count when deleting."""
        article = instance.article
        article.comments_count = max(0, article.comments_count - 1)
        article.save(update_fields=['comments_count'])
        instance.delete()


class ArticleLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for article likes (read-only)."""
    
    queryset = ArticleLike.objects.select_related('user', 'article')
    serializer_class = ArticleLikeSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by article or user."""
        queryset = self.queryset
        
        article_slug = self.request.query_params.get('article')
        if article_slug:
            queryset = queryset.filter(article__slug=article_slug)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')