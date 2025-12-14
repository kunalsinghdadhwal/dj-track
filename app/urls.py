"""
Task Tracker App URL Configuration

This module defines URL patterns for the Task Tracker app,
including task CRUD endpoints and user registration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, UserRegistrationView, UserProfileView


# Create router for ViewSets
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # User registration
    path(
        'register/',
        UserRegistrationView.as_view(),
        name='user-register'
    ),

    # User profile
    path(
        'profile/',
        UserProfileView.as_view(),
        name='user-profile'
    ),

    # ViewSet routes (tasks)
    path('', include(router.urls)),
]
