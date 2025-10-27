from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register all viewsets
router.register(r'categories', views.PostCategoryViewSet, basename='postcategory')
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.PostCommentViewSet, basename='postcomment')
router.register(r'post-likes', views.PostLikeViewSet, basename='postlike')
router.register(r'comment-likes', views.CommentLikeViewSet, basename='commentlike')
router.register(r'shares', views.PostShareViewSet, basename='postshare')
router.register(r'reports', views.PostReportViewSet, basename='postreport')
router.register(r'tags', views.PostTagViewSet, basename='posttag')
router.register(r'stats', views.PostStatsViewSet, basename='poststats')

urlpatterns = [
    path('', include(router.urls)),
]