"""
Task Tracker Serializers

This module defines serializers for User registration, authentication,
and Task operations.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Task


class EmailLoginSerializer(serializers.Serializer):
    """
    Serializer for email-based login.

    Authenticates users using email and password instead of username.
    """

    email = serializers.EmailField(
        required=True,
        help_text='User email address'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='User password'
    )

    def validate(self, attrs):
        """Validate email and password and return the user."""
        email = attrs.get('email')
        password = attrs.get('password')

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No user found with this email address.'
            })

        # Authenticate with username (Django's default)
        user = authenticate(
            request=self.context.get('request'),
            username=user.username,
            password=password
        )

        if not user:
            raise serializers.ValidationError({
                'password': 'Invalid password.'
            })

        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'User account is disabled.'
            })

        attrs['user'] = user
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for token refresh.

    When using cookies, the refresh token is read from cookies automatically,
    but this serializer can also accept it in the body for API clients.
    """

    refresh = serializers.CharField(
        required=False,
        help_text='Refresh token (optional if using cookies)'
    )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout.

    Optionally accepts refresh token to blacklist it.
    """

    refresh = serializers.CharField(
        required=False,
        help_text='Refresh token to blacklist (optional if using cookies)'
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles creating new users with validated passwords.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='User password (min 8 characters)'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirm password'
    )
    email = serializers.EmailField(
        required=True,
        help_text='User email address'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {'help_text': 'Unique username'},
        }

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.'
            )
        return value

    def validate_username(self, value):
        """Ensure username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with this username already exists.'
            )
        return value

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user information.

    Used for displaying user details in responses.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.

    Handles CRUD operations for tasks with validation.
    """

    user = UserSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'due_date',
            'is_overdue',
            'created_at',
            'updated_at',
            'user',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate_title(self, value):
        """Ensure title is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError(
                'Title cannot be empty or whitespace only.'
            )
        return value.strip()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks.

    Simplified serializer for task creation with proper field handling.
    """

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        """Ensure title is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError(
                'Title cannot be empty or whitespace only.'
            )
        return value.strip()

    def create(self, validated_data):
        """Create task and assign to current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for task lists.

    Returns minimal data for better performance in list views.
    """

    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'status',
            'priority',
            'due_date',
            'is_overdue',
            'created_at',
        ]
        read_only_fields = fields
