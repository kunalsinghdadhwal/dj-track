"""
Task Tracker API URL Configuration

This module defines the root URL patterns for the Task Tracker API,
including JWT authentication endpoints, API documentation, and app routes.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from drf_spectacular.utils import extend_schema

# Extend schema for JWT views
TokenObtainPairView = extend_schema(
    tags=['Authentication'],
    summary='Obtain JWT token pair',
    description='Get access and refresh tokens using username and password.',
)(TokenObtainPairView)

TokenRefreshView = extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Get a new access token using a valid refresh token.',
)(TokenRefreshView)

TokenVerifyView = extend_schema(
    tags=['Authentication'],
    summary='Verify token',
    description='Verify that a token is valid.',
)(TokenVerifyView)


def scalar_docs_view(request):
    """
    Serve Scalar API documentation.

    Renders a beautiful, interactive API documentation page
    using the Scalar library.
    """
    from django.http import HttpResponse

    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Task Tracker API - Documentation</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📋</text></svg>">
</head>
<body>
    <script
        id="api-reference"
        data-url="/api/schema/"
        data-configuration='{
            "theme": "purple",
            "layout": "modern",
            "showSidebar": true,
            "hideModels": false,
            "hideDownloadButton": false,
            "hiddenClients": [],
            "defaultHttpClient": {
                "targetKey": "python",
                "clientKey": "requests"
            }
        }'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>
'''
    return HttpResponse(html)


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # JWT Authentication endpoints
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'api/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),

    # OpenAPI Schema
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),

    # API Documentation (Scalar - modern interactive docs)
    path(
        'docs/',
        scalar_docs_view,
        name='scalar-docs'
    ),

    # Alternative documentation views (optional)
    path(
        'api/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'api/docs/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

    # App routes (tasks, registration, etc.)
    path('api/', include('app.urls')),
]
