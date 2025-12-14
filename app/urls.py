"""
Task Tracker App URL Configuration

This module defines URL patterns for the Task Tracker app,
including authentication, user management, and task endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication views
    LoginView,
    LogoutView,
    TokenRefreshView,
    TokenVerifyView,
    # User views
    UserRegistrationView,
    UserProfileView,
    # Task views
    TaskViewSet,
)


# Create router for ViewSets
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # ==========================================================================
    # Authentication endpoints (cookie-based JWT)
    # ==========================================================================
    path(
        'auth/register/',
        UserRegistrationView.as_view(),
        name='auth-register'
    ),
    path(
        'auth/login/',
        LoginView.as_view(),
        name='auth-login'
    ),
    path(
        'auth/logout/',
        LogoutView.as_view(),
        name='auth-logout'
    ),
    path(
        'auth/refresh/',
        TokenRefreshView.as_view(),
        name='auth-refresh'
    ),
    path(
        'auth/verify/',
        TokenVerifyView.as_view(),
        name='auth-verify'
    ),

    # ==========================================================================
    # User endpoints
    # ==========================================================================
    path(
        'auth/me/',
        UserProfileView.as_view(),
        name='auth-me'
    ),

    # ==========================================================================
    # Task endpoints (via router)
    # ==========================================================================
    path('', include(router.urls)),
]
