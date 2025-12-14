"""
Task Tracker Views

This module defines ViewSets and API views for the Task Tracker API,
including cookie-based JWT authentication endpoints.
"""

from django.conf import settings
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from .models import Task
from .serializers import (
    EmailLoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
)
from .permissions import IsTaskOwner
from .filters import TaskFilter


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_auth_cookies(response, tokens):
    """Set HTTP-only cookies with JWT tokens."""
    jwt_settings = settings.SIMPLE_JWT

    # Set access token cookie
    response.set_cookie(
        key=jwt_settings['AUTH_COOKIE'],
        value=tokens['access'],
        max_age=int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        secure=jwt_settings['AUTH_COOKIE_SECURE'],
        httponly=jwt_settings['AUTH_COOKIE_HTTP_ONLY'],
        samesite=jwt_settings['AUTH_COOKIE_SAMESITE'],
        path=jwt_settings['AUTH_COOKIE_PATH'],
    )

    # Set refresh token cookie
    response.set_cookie(
        key=jwt_settings['AUTH_COOKIE_REFRESH'],
        value=tokens['refresh'],
        max_age=int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        secure=jwt_settings['AUTH_COOKIE_SECURE'],
        httponly=jwt_settings['AUTH_COOKIE_HTTP_ONLY'],
        samesite=jwt_settings['AUTH_COOKIE_SAMESITE'],
        path=jwt_settings['AUTH_COOKIE_PATH'],
    )

    return response


def clear_auth_cookies(response):
    """Clear authentication cookies."""
    jwt_settings = settings.SIMPLE_JWT

    response.delete_cookie(
        key=jwt_settings['AUTH_COOKIE'],
        path=jwt_settings['AUTH_COOKIE_PATH'],
    )
    response.delete_cookie(
        key=jwt_settings['AUTH_COOKIE_REFRESH'],
        path=jwt_settings['AUTH_COOKIE_PATH'],
    )

    return response


@extend_schema(tags=['Authentication'])
class LoginView(APIView):
    """
    Login with email and password.

    Returns JWT tokens stored in HTTP-only cookies.
    Also returns tokens in response body for API clients.
    """

    permission_classes = [AllowAny]
    serializer_class = EmailLoginSerializer

    @extend_schema(
        summary='Login',
        description='Authenticate with email and password. Tokens are set in HTTP-only cookies.',
        request=EmailLoginSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user': {'type': 'object'},
                    'access': {'type': 'string'},
                    'refresh': {'type': 'string'},
                }
            },
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'john@example.com',
                    'password': 'SecurePass123!'
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        """Handle login request."""
        serializer = EmailLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)

        response_data = {
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        return set_auth_cookies(response, tokens)


@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    """
    Logout and invalidate tokens.

    Clears HTTP-only cookies and blacklists the refresh token.
    """

    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    @extend_schema(
        summary='Logout',
        description='Logout and clear authentication cookies. Optionally blacklist refresh token.',
        request=LogoutSerializer,
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        }
    )
    def post(self, request):
        """Handle logout request."""
        jwt_settings = settings.SIMPLE_JWT

        # Try to get refresh token from cookie or request body
        refresh_token = request.COOKIES.get(jwt_settings['AUTH_COOKIE_REFRESH'])
        if not refresh_token:
            serializer = LogoutSerializer(data=request.data)
            if serializer.is_valid():
                refresh_token = serializer.validated_data.get('refresh')

        # Try to blacklist the refresh token
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already blacklisted or invalid

        response = Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
        return clear_auth_cookies(response)


@extend_schema(tags=['Authentication'])
class TokenRefreshView(APIView):
    """
    Refresh access token.

    Uses refresh token from cookie or request body to generate new tokens.
    """

    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    @extend_schema(
        summary='Refresh Token',
        description='Get new access token using refresh token (from cookie or body).',
        request=TokenRefreshSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'access': {'type': 'string'},
                    'refresh': {'type': 'string'},
                }
            },
            401: OpenApiTypes.OBJECT,
        }
    )
    def post(self, request):
        """Handle token refresh request."""
        jwt_settings = settings.SIMPLE_JWT

        # Try to get refresh token from cookie first, then body
        refresh_token = request.COOKIES.get(jwt_settings['AUTH_COOKIE_REFRESH'])
        if not refresh_token:
            serializer = TokenRefreshSerializer(data=request.data)
            if serializer.is_valid():
                refresh_token = serializer.validated_data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token not provided'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            from django.contrib.auth.models import User

            refresh = RefreshToken(refresh_token)

            # Get new access token
            new_access = str(refresh.access_token)

            # For rotation, we need to create a new refresh token
            if jwt_settings.get('ROTATE_REFRESH_TOKENS', False):
                # Get the user from the token
                user_id = refresh.payload.get('user_id')
                user = User.objects.get(id=user_id)

                # Blacklist the old refresh token
                try:
                    refresh.blacklist()
                except Exception:
                    pass  # Token might already be blacklisted

                # Create new refresh token
                new_refresh = RefreshToken.for_user(user)
                tokens = {
                    'access': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                }
            else:
                tokens = {
                    'access': new_access,
                    'refresh': str(refresh),
                }

            response_data = {
                'message': 'Token refreshed successfully',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
            }

            response = Response(response_data, status=status.HTTP_200_OK)
            return set_auth_cookies(response, tokens)

        except (TokenError, User.DoesNotExist) as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@extend_schema(tags=['Authentication'])
class TokenVerifyView(APIView):
    """
    Verify if access token is valid.

    Checks token from cookie or Authorization header.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary='Verify Token',
        description='Check if the current access token is valid.',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'valid': {'type': 'boolean'},
                    'user': {'type': 'object'},
                }
            },
            401: OpenApiTypes.OBJECT,
        }
    )
    def get(self, request):
        """Verify the current token."""
        jwt_settings = settings.SIMPLE_JWT

        # Try to authenticate using the cookie
        from .authentication import CookieJWTAuthentication
        auth = CookieJWTAuthentication()

        try:
            result = auth.authenticate(request)
            if result:
                user, token = result
                return Response({
                    'valid': True,
                    'user': UserSerializer(user).data,
                })
        except Exception:
            pass

        return Response(
            {'valid': False, 'error': 'Invalid or expired token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(tags=['Users'])
class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.

    Creates a new user account with username, email, and password.
    No authentication required for this endpoint.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Register a new user',
        description='Create a new user account. Returns user details on success.',
        request=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Registration Request',
                summary='New user registration',
                value={
                    'username': 'johndoe',
                    'email': 'john@example.com',
                    'password': 'SecurePass123!',
                    'password_confirm': 'SecurePass123!'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Registration Response',
                summary='Successful registration',
                value={
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com',
                    'date_joined': '2025-01-15T10:30:00Z'
                },
                response_only=True,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Users'])
class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve the current user's profile.

    Returns the authenticated user's information.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Get current user profile',
        description='Returns the authenticated user\'s profile information.',
        responses={200: UserSerializer},
    )
    def get(self, request, *args, **kwargs):
        """Return current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary='List all tasks',
        description='''
        Returns a paginated list of tasks owned by the authenticated user.

        **Filtering:**
        - `status`: Filter by status (todo, in_progress, done)
        - `priority`: Filter by priority (low, medium, high)
        - `due_date`: Filter by exact due date
        - `due_date_before`: Tasks due on or before date
        - `due_date_after`: Tasks due on or after date
        - `is_overdue`: Filter overdue tasks (true/false)

        **Searching:**
        - `search`: Search in title and description

        **Ordering:**
        - `ordering`: Order by created_at, due_date, priority, status
        - Prefix with `-` for descending (e.g., `-created_at`)
        ''',
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                enum=['todo', 'in_progress', 'done'],
                description='Filter by task status',
            ),
            OpenApiParameter(
                name='priority',
                type=str,
                enum=['low', 'medium', 'high'],
                description='Filter by task priority',
            ),
            OpenApiParameter(
                name='search',
                type=str,
                description='Search in title and description',
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with - for desc)',
            ),
        ],
        tags=['Tasks'],
    ),
    create=extend_schema(
        summary='Create a new task',
        description='Create a new task for the authenticated user.',
        request=TaskCreateSerializer,
        responses={201: TaskSerializer},
        examples=[
            OpenApiExample(
                'Create Task',
                value={
                    'title': 'Complete project documentation',
                    'description': 'Write comprehensive API documentation',
                    'status': 'todo',
                    'priority': 'high',
                    'due_date': '2025-02-01'
                },
                request_only=True,
            ),
        ],
        tags=['Tasks'],
    ),
    retrieve=extend_schema(
        summary='Get a task',
        description='Retrieve a specific task by ID. Only the owner can access.',
        responses={200: TaskSerializer, 404: OpenApiTypes.OBJECT},
        tags=['Tasks'],
    ),
    update=extend_schema(
        summary='Update a task',
        description='Fully update a task. Only the owner can modify.',
        request=TaskCreateSerializer,
        responses={200: TaskSerializer},
        tags=['Tasks'],
    ),
    partial_update=extend_schema(
        summary='Partially update a task',
        description='Update specific fields of a task. Only the owner can modify.',
        request=TaskCreateSerializer,
        responses={200: TaskSerializer},
        tags=['Tasks'],
    ),
    destroy=extend_schema(
        summary='Delete a task',
        description='Delete a task. Only the owner can delete.',
        responses={204: None},
        tags=['Tasks'],
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.

    Provides CRUD operations for tasks with filtering, searching,
    and ordering capabilities. All operations are restricted to
    the authenticated user's own tasks.
    """

    permission_classes = [IsAuthenticated, IsTaskOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return tasks owned by the current user only.

        This ensures users can only see and manage their own tasks.
        """
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - list: TaskListSerializer (lightweight)
        - create: TaskCreateSerializer
        - other: TaskSerializer (full details)
        """
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """Set the user when creating a task."""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary='Get task statistics',
        description='Returns statistics about the user\'s tasks.',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total': {'type': 'integer'},
                    'by_status': {
                        'type': 'object',
                        'properties': {
                            'todo': {'type': 'integer'},
                            'in_progress': {'type': 'integer'},
                            'done': {'type': 'integer'},
                        }
                    },
                    'by_priority': {
                        'type': 'object',
                        'properties': {
                            'low': {'type': 'integer'},
                            'medium': {'type': 'integer'},
                            'high': {'type': 'integer'},
                        }
                    },
                    'overdue': {'type': 'integer'},
                }
            }
        },
        tags=['Tasks'],
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get task statistics for the authenticated user.

        Returns counts by status, priority, and overdue tasks.
        """
        from django.db.models import Count, Q
        from django.utils import timezone

        queryset = self.get_queryset()

        # Get counts by status
        status_counts = queryset.values('status').annotate(count=Count('id'))
        by_status = {item['status']: item['count'] for item in status_counts}

        # Get counts by priority
        priority_counts = queryset.values('priority').annotate(count=Count('id'))
        by_priority = {item['priority']: item['count'] for item in priority_counts}

        # Get overdue count
        overdue_count = queryset.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status=Task.Status.DONE).count()

        return Response({
            'total': queryset.count(),
            'by_status': {
                'todo': by_status.get('todo', 0),
                'in_progress': by_status.get('in_progress', 0),
                'done': by_status.get('done', 0),
            },
            'by_priority': {
                'low': by_priority.get('low', 0),
                'medium': by_priority.get('medium', 0),
                'high': by_priority.get('high', 0),
            },
            'overdue': overdue_count,
        })

    @extend_schema(
        summary='Mark task as complete',
        description='Quick action to mark a task as done.',
        responses={200: TaskSerializer},
        tags=['Tasks'],
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as complete."""
        task = self.get_object()
        task.status = Task.Status.DONE
        task.save()
        return Response(TaskSerializer(task).data)
