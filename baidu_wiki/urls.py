"""baidu_wiki URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('wiki_detail.html', TemplateView.as_view(template_name='wiki_detail.html'), name='wiki_detail'),
    path('wiki_edit.html', TemplateView.as_view(template_name='wiki_edit.html'), name='wiki_edit'),
    path('search.html', TemplateView.as_view(template_name='search.html'), name='search'),
    path('user_profile.html', TemplateView.as_view(template_name='user_profile.html'), name='user_profile'),
    path('notifications.html', TemplateView.as_view(template_name='notifications.html'), name='notifications'),
    path('api/auth/', include('users.urls')),
    path('api/wiki/', include('wiki.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/search/', include('search.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)