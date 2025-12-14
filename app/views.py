"""
Task Tracker Views

This module defines ViewSets and API views for the Task Tracker API.
"""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    UserRegistrationSerializer,
    UserSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
)
from .permissions import IsTaskOwner
from .filters import TaskFilter


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
