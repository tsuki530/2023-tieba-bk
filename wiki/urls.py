from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register all viewsets
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'versions', views.ArticleVersionViewSet, basename='articleversion')
router.register(r'comments', views.ArticleCommentViewSet, basename='articlecomment')
router.register(r'likes', views.ArticleLikeViewSet, basename='articlelike')

urlpatterns = [
    path('', include(router.urls)),
]