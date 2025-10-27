from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404

from .models import CustomUser, UserProfile, Follow
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, FollowSerializer, PasswordChangeSerializer
)


class UserRegistrationView(APIView):
    """User registration view."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Log user in
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login view."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create or get auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Log user in
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """User logout view."""
    
    def post(self, request):
        # Delete auth token
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        
        # Log user out
        logout(request)
        
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """User profile view."""
    
    def get(self, request):
        """Get current user profile."""
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response({
                'is_authenticated': False,
                'message': 'Please log in to view your profile.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    def put(self, request):
        """Update current user profile."""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """User detail view for public profiles."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """Get user public profile."""
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class FollowUserView(APIView):
    """Follow/unfollow user view."""
    
    def post(self, request, user_id):
        """Follow a user."""
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        
        if request.user == user_to_follow:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            followed=user_to_follow
        )
        
        if created:
            # Update counts
            request.user.following_count = Follow.objects.filter(follower=request.user).count()
            user_to_follow.followers_count = Follow.objects.filter(followed=user_to_follow).count()
            request.user.save()
            user_to_follow.save()
            
            return Response({'message': f'You are now following {user_to_follow.get_display_name()}.'})
        
        return Response({'message': 'You are already following this user.'})
    
    def delete(self, request, user_id):
        """Unfollow a user."""
        user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
        
        follow = Follow.objects.filter(
            follower=request.user,
            followed=user_to_unfollow
        ).first()
        
        if follow:
            follow.delete()
            
            # Update counts
            request.user.following_count = Follow.objects.filter(follower=request.user).count()
            user_to_unfollow.followers_count = Follow.objects.filter(followed=user_to_unfollow).count()
            request.user.save()
            user_to_unfollow.save()
            
            return Response({'message': f'You have unfollowed {user_to_unfollow.get_display_name()}.'})
        
        return Response(
            {'error': 'You are not following this user.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserFollowersView(APIView):
    """Get user's followers."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """Get list of user's followers."""
        user = get_object_or_404(CustomUser, id=user_id)
        followers = Follow.objects.filter(followed=user).select_related('follower')
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)


class UserFollowingView(APIView):
    """Get users that a user is following."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """Get list of users that the user is following."""
        user = get_object_or_404(CustomUser, id=user_id)
        following = Follow.objects.filter(follower=user).select_related('followed')
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password."""
    serializer = PasswordChangeSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check old password
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        # Update auth token
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        
        token, created = Token.objects.get_or_create(user=request.user)
        
        return Response({
            'message': 'Password changed successfully.',
            'token': token.key
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)