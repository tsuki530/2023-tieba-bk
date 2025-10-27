from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile, Follow

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'password_confirm')
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), 
                             email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled.')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Email and password are required.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'reputation', 'level', 'articles_created', 
                           'articles_edited', 'posts_created', 'comments_created')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    
    profile = UserProfileSerializer(read_only=True)
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'avatar', 'bio', 'location', 'website', 'followers_count', 
                 'following_count', 'last_active', 'date_joined', 'profile')
        read_only_fields = ('id', 'last_active', 'date_joined', 'followers_count', 
                           'following_count')


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""
    
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ('id', 'follower', 'followed', 'created_at')
        read_only_fields = ('id', 'created_at')


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password change."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs