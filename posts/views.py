from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    PostCategory, Post, PostLike, PostComment, CommentLike, 
    PostShare, PostReport, PostTag
)
from .serializers import *

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination for consistent results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for post categories."""
    
    queryset = PostCategory.objects.annotate(
        post_count=Count('posts', distinct=True)
    ).order_by('name')
    serializer_class = PostCategorySerializer
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for posts."""
    
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags')
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        elif self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = self.queryset.filter(status='published')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by author
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Filter by post type
        post_type = self.request.query_params.get('type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        # Search by title and content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Order by pinned first, then by creation date
        queryset = queryset.order_by('-is_pinned', '-created_at')
        
        return queryset
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Set author and handle published_at."""
        post = serializer.save(author=self.request.user)
        if post.status == 'published' and not post.published_at:
            post.published_at = timezone.now()
            post.save()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a post."""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(
            post=post, 
            user=request.user
        )
        
        if not created:
            # Unlike if already liked
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            message = 'Post unliked'
        else:
            post.likes_count += 1
            message = 'Post liked'
        
        post.save(update_fields=['likes_count'])
        return Response({'message': message, 'likes_count': post.likes_count})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment post view count."""
        post = self.get_object()
        post.increment_views()
        return Response({'views_count': post.views_count})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts."""
        featured_posts = self.get_queryset().filter(
            is_featured=True, 
            status='published'
        )[:10]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned posts."""
        pinned_posts = self.get_queryset().filter(
            is_pinned=True, 
            status='published'
        )
        serializer = self.get_serializer(pinned_posts, many=True)
        return Response(serializer.data)


class PostCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for post comments."""
    
    queryset = PostComment.objects.select_related('author', 'post', 'parent')
    serializer_class = PostCommentSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PostCommentCreateSerializer
        return PostCommentSerializer
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = self.queryset.filter(is_approved=True)
        
        # Filter by post
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
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
        """Set author and update post comment count."""
        comment = serializer.save(author=self.request.user)
        
        # Update post comment count
        post = comment.post
        post.comments_count += 1
        post.save(update_fields=['comments_count'])
    
    def perform_destroy(self, instance):
        """Update post comment count when deleting."""
        post = instance.post
        post.comments_count = max(0, post.comments_count - 1)
        post.save(update_fields=['comments_count'])
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a comment."""
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(
            comment=comment, 
            user=request.user
        )
        
        if not created:
            # Unlike if already liked
            like.delete()
            comment.likes_count = max(0, comment.likes_count - 1)
            message = 'Comment unliked'
        else:
            comment.likes_count += 1
            message = 'Comment liked'
        
        comment.save(update_fields=['likes_count'])
        return Response({'message': message, 'likes_count': comment.likes_count})


class PostLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for post likes (read-only)."""
    
    queryset = PostLike.objects.select_related('user', 'post')
    serializer_class = PostLikeSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by post or user."""
        queryset = self.queryset
        
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')


class CommentLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for comment likes (read-only)."""
    
    queryset = CommentLike.objects.select_related('user', 'comment')
    serializer_class = CommentLikeSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by comment or user."""
        queryset = self.queryset
        
        comment_id = self.request.query_params.get('comment')
        if comment_id:
            queryset = queryset.filter(comment_id=comment_id)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')


class PostShareViewSet(viewsets.ModelViewSet):
    """ViewSet for post shares."""
    
    queryset = PostShare.objects.select_related('user', 'post')
    serializer_class = PostShareSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PostShareCreateSerializer
        return PostShareSerializer
    
    def get_queryset(self):
        """Filter by post or user."""
        queryset = self.queryset
        
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Set user and update post share count."""
        share = serializer.save(user=self.request.user)
        
        # Update post share count
        post = share.post
        post.shares_count += 1
        post.save(update_fields=['shares_count'])


class PostReportViewSet(viewsets.ModelViewSet):
    """ViewSet for post reports."""
    
    queryset = PostReport.objects.select_related('reporter', 'post', 'comment')
    serializer_class = PostReportSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PostReportCreateSerializer
        return PostReportSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = self.queryset
        
        # Regular users can only see their own reports
        if not self.request.user.is_staff:
            queryset = queryset.filter(reporter=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set reporter and update reported count."""
        report = serializer.save(reporter=self.request.user)
        
        # Update reported count on target
        if report.post:
            report.post.reported_count += 1
            report.post.save(update_fields=['reported_count'])
        elif report.comment:
            report.comment.reported_count += 1
            report.comment.save(update_fields=['reported_count'])


class PostTagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for post tags (read-only)."""
    
    queryset = PostTag.objects.all()
    serializer_class = PostTagSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter by search term."""
        queryset = self.queryset
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')


class PostStatsViewSet(viewsets.ViewSet):
    """ViewSet for post statistics."""
    
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """Get overall post statistics."""
        total_posts = Post.objects.filter(status='published').count()
        total_comments = PostComment.objects.filter(is_approved=True).count()
        total_likes = PostLike.objects.count()
        total_views = Post.objects.aggregate(total_views=models.Sum('views_count'))['total_views'] or 0
        
        # Get popular posts (by views)
        popular_posts = Post.objects.filter(status='published').order_by('-views_count')[:5]
        
        # Get recent posts
        recent_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]
        
        data = {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'total_views': total_views,
            'popular_posts': PostListSerializer(popular_posts, many=True, context={'request': request}).data,
            'recent_posts': PostListSerializer(recent_posts, many=True, context={'request': request}).data,
        }
        
        return Response(data)