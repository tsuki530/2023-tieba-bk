from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchViewSet, AdvancedSearchViewSet

router = DefaultRouter()
router.register(r'search', SearchViewSet, basename='search')
router.register(r'advanced-search', AdvancedSearchViewSet, basename='advanced-search')

urlpatterns = [
    path('', include(router.urls)),
]