"""
Django settings for Task Tracker API project.

This is a production-ready configuration for a Task Tracker REST API
using Django REST Framework with JWT authentication.
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# In production, use environment variable: os.environ.get('SECRET_KEY')
SECRET_KEY = 'django-insecure-2fh^=g^wv0zxyf9ieczju@^1sk@^j6(&z#lo_r35uku#f$b4k&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # For logout/token invalidation
    'django_filters',
    'drf_spectacular',
    'corsheaders',

    # Local apps
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'simplejwt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'simplejwt.wsgi.application'


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# SQLite for development - easy to switch to PostgreSQL for production

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # PostgreSQL configuration (uncomment and configure for production):
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': os.environ.get('DB_NAME', 'tasktracker'),
    #     'USER': os.environ.get('DB_USER', 'postgres'),
    #     'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    #     'HOST': os.environ.get('DB_HOST', 'localhost'),
    #     'PORT': os.environ.get('DB_PORT', '5432'),
    # }
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    # Authentication - Cookie-based JWT with fallback to header
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.authentication.CookieJWTAuthentication',
    ],

    # Permissions - require authentication by default
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # Filtering, searching, and ordering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Schema generation for drf-spectacular
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # Exception handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}


# =============================================================================
# SIMPLE JWT CONFIGURATION
# =============================================================================

SIMPLE_JWT = {
    # Token lifetimes - short-lived access tokens for security
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # Rotation settings
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # Algorithm
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    # Token headers (fallback for API clients)
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # User identification
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    # Token claims
    'TOKEN_TYPE_CLAIM': 'token_type',

    # Cookie settings for browser-based authentication
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    'AUTH_COOKIE_SECURE': not DEBUG,  # True in production (HTTPS only)
    'AUTH_COOKIE_HTTP_ONLY': True,    # Prevents JavaScript access (XSS protection)
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',    # CSRF protection
}


# =============================================================================
# DRF-SPECTACULAR (OPENAPI) CONFIGURATION
# =============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Task Tracker API',
    'DESCRIPTION': '''
## Task Tracker REST API

A production-ready RESTful API for managing tasks with JWT authentication stored in HTTP-only cookies.

### Features
- **User Registration & Authentication**: Secure JWT-based authentication with cookies
- **Email-based Login**: Login using email and password
- **Task Management**: Full CRUD operations for personal tasks
- **Filtering & Search**: Filter by status, priority, due date; search by title/description
- **Pagination**: Paginated responses for large datasets

### Authentication
This API uses HTTP-only cookies for secure token storage:
- **Browser clients**: Tokens are automatically stored in secure cookies
- **API clients**: Can still use `Authorization: Bearer <token>` header

### Quick Start
1. Register a new user at `POST /api/auth/register/`
2. Login at `POST /api/auth/login/` with email and password
3. Cookies are automatically set - no manual token handling needed!
4. Logout at `POST /api/auth/logout/` to clear cookies
5. Refresh tokens at `POST /api/auth/refresh/`
''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Contact information
    'CONTACT': {
        'name': 'Kunal Singh Dadhwal',
        'email': 'kunal@example.com',
    },

    # License
    'LICENSE': {
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT',
    },

    # Tags for organizing endpoints
    'TAGS': [
        {'name': 'Authentication', 'description': 'JWT token operations'},
        {'name': 'Users', 'description': 'User registration and profile'},
        {'name': 'Tasks', 'description': 'Task management operations'},
    ],

    # Security schemes
    'SECURITY': [{'bearerAuth': []}],

    # Component settings
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,

    # Schema customization
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
    },

    # Enum naming
    'ENUM_NAME_OVERRIDES': {
        'StatusEnum': 'app.models.Task.Status',
        'PriorityEnum': 'app.models.Task.Priority',
    },
}


# =============================================================================
# CORS CONFIGURATION (for frontend integration)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Allow cookies to be sent with cross-origin requests
CORS_ALLOW_CREDENTIALS = True

# Expose headers to frontend
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
