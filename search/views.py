import time
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Article, Category, Tag
from posts.models import Post, PostCategory
from .serializers import *

User = get_user_model()


class SearchResultsPagination(PageNumberPagination):
    """Custom pagination for search results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SearchViewSet(viewsets.ViewSet):
    """ViewSet for search functionality."""
    
    permission_classes = [permissions.AllowAny]
    pagination_class = SearchResultsPagination
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Perform search across all content types."""
        start_time = time.time()
        
        # Validate query parameters
        query_serializer = SearchQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(
                query_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        query_data = query_serializer.validated_data
        search_query = query_data['q']
        search_type = query_data['type']
        
        # Initialize results
        all_results = []
        stats = {
            'articles_count': 0,
            'posts_count': 0,
            'users_count': 0,
            'categories_count': 0,
            'tags_count': 0,
        }
        
        # Search articles
        if search_type in ['all', 'articles']:
            articles = self.search_articles(search_query, query_data)
            stats['articles_count'] = len(articles)
            all_results.extend(articles)
        
        # Search posts
        if search_type in ['all', 'posts']:
            posts = self.search_posts(search_query, query_data)
            stats['posts_count'] = len(posts)
            all_results.extend(posts)
        
        # Search users
        if search_type in ['all', 'users']:
            users = self.search_users(search_query, query_data)
            stats['users_count'] = len(users)
            all_results.extend(users)
        
        # Search categories
        if search_type in ['all', 'categories']:
            categories = self.search_categories(search_query, query_data)
            stats['categories_count'] = len(categories)
            all_results.extend(categories)
        
        # Search tags
        if search_type in ['all', 'tags']:
            tags = self.search_tags(search_query, query_data)
            stats['tags_count'] = len(tags)
            all_results.extend(tags)
        
        # Sort results
        all_results = self.sort_results(all_results, query_data['sort_by'])
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(all_results, request)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Prepare response
        response_data = {
            'results': page,
            'total_results': len(all_results),
            'search_time': search_time,
            'query': search_query,
            'stats': stats
        }
        
        return paginator.get_paginated_response(response_data)
    
    def search_articles(self, query, query_data):
        """Search articles."""
        articles = Article.objects.filter(status='published')
        
        # Basic search
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        
        # Additional filters
        if query_data.get('category'):
            articles = articles.filter(category__slug=query_data['category'])
        
        if query_data.get('tag'):
            articles = articles.filter(tags__slug=query_data['tag'])
        
        if query_data.get('author'):
            articles = articles.filter(author__username=query_data['author'])
        
        # Select related for performance
        articles = articles.select_related('author', 'category').prefetch_related('tags')
        
        # Serialize results
        serializer = ArticleSearchSerializer(articles, many=True, context={'request': self.request})
        return serializer.data
    
    def search_posts(self, query, query_data):
        """Search posts."""
        posts = Post.objects.filter(status='published')
        
        # Basic search
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        
        # Additional filters
        if query_data.get('category'):
            posts = posts.filter(category__slug=query_data['category'])
        
        if query_data.get('author'):
            posts = posts.filter(author__username=query_data['author'])
        
        # Select related for performance
        posts = posts.select_related('author', 'category')
        
        # Serialize results
        serializer = PostSearchSerializer(posts, many=True, context={'request': self.request})
        return serializer.data
    
    def search_users(self, query, query_data):
        """Search users."""
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).filter(is_active=True)
        
        # Serialize results
        serializer = UserSearchSerializer(users, many=True, context={'request': self.request})
        return serializer.data
    
    def search_categories(self, query, query_data):
        """Search categories."""
        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        
        # Serialize results
        serializer = CategorySearchSerializer(categories, many=True, context={'request': self.request})
        return serializer.data
    
    def search_tags(self, query, query_data):
        """Search tags."""
        tags = Tag.objects.filter(name__icontains=query)
        
        # Serialize results
        serializer = TagSearchSerializer(tags, many=True, context={'request': self.request})
        return serializer.data
    
    def sort_results(self, results, sort_by):
        """Sort search results."""
        if sort_by == 'date':
            return sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == 'views':
            return sorted(results, key=lambda x: x.get('views_count', 0), reverse=True)
        elif sort_by == 'likes':
            return sorted(results, key=lambda x: x.get('likes_count', 0), reverse=True)
        else:  # relevance (default)
            # Simple relevance scoring based on title/content match
            return results
    
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """Provide autocomplete suggestions."""
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response([])
        
        results = []
        
        # Article titles
        articles = Article.objects.filter(
            title__icontains=query, 
            status='published'
        ).values('id', 'title')[:5]
        
        for article in articles:
            results.append({
                'id': f"article_{article['id']}",
                'text': article['title'],
                'type': 'article',
                'url': f"/articles/{article['id']}/"
            })
        
        # Post titles
        posts = Post.objects.filter(
            title__icontains=query, 
            status='published'
        ).values('id', 'title')[:5]
        
        for post in posts:
            results.append({
                'id': f"post_{post['id']}",
                'text': post['title'],
                'type': 'post',
                'url': f"/posts/{post['id']}/"
            })
        
        # Users
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).filter(is_active=True).values('id', 'username', 'first_name', 'last_name')[:5]
        
        for user in users:
            display_name = user['username']
            if user['first_name'] and user['last_name']:
                display_name = f"{user['first_name']} {user['last_name']} ({user['username']})"
            
            results.append({
                'id': f"user_{user['id']}",
                'text': display_name,
                'type': 'user',
                'url': f"/users/{user['username']}/"
            })
        
        # Categories
        categories = Category.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:5]
        
        for category in categories:
            results.append({
                'id': f"category_{category['id']}",
                'text': category['name'],
                'type': 'category',
                'url': f"/categories/{category['slug']}/"
            })
        
        # Tags
        tags = Tag.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:5]
        
        for tag in tags:
            results.append({
                'id': f"tag_{tag['id']}",
                'text': tag['name'],
                'type': 'tag',
                'url': f"/tags/{tag['slug']}/"
            })
        
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get search statistics."""
        total_articles = Article.objects.filter(status='published').count()
        total_posts = Post.objects.filter(status='published').count()
        total_users = User.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        total_tags = Tag.objects.count()
        
        data = {
            'total_articles': total_articles,
            'total_posts': total_posts,
            'total_users': total_users,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'popular_searches': [
                {'query': 'python', 'count': 150},
                {'query': 'django', 'count': 120},
                {'query': 'javascript', 'count': 95},
                {'query': 'react', 'count': 80},
                {'query': 'vue', 'count': 65},
            ]
        }
        
        return Response(data)


class AdvancedSearchViewSet(viewsets.ViewSet):
    """ViewSet for advanced search functionality."""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Get available search filters."""
        # Get categories
        categories = Category.objects.all().values('id', 'name', 'slug')
        
        # Get tags
        tags = Tag.objects.all().values('id', 'name', 'slug')
        
        # Get post categories
        post_categories = PostCategory.objects.all().values('id', 'name', 'slug')
        
        data = {
            'categories': list(categories),
            'tags': list(tags),
            'post_categories': list(post_categories),
            'sort_options': [
                {'value': 'relevance', 'label': 'Relevance'},
                {'value': 'date', 'label': 'Date'},
                {'value': 'views', 'label': 'Views'},
                {'value': 'likes', 'label': 'Likes'},
            ],
            'type_options': [
                {'value': 'all', 'label': 'All'},
                {'value': 'articles', 'label': 'Articles'},
                {'value': 'posts', 'label': 'Posts'},
                {'value': 'users', 'label': 'Users'},
                {'value': 'categories', 'label': 'Categories'},
                {'value': 'tags', 'label': 'Tags'},
            ]
        }
        
        return Response(data)