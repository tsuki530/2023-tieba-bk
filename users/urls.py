from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # User profiles
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Follow relationships
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow_user'),
    path('users/<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user_followers'),
    path('users/<int:user_id>/following/', views.UserFollowingView.as_view(), name='user_following'),
]