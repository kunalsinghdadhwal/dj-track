# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Task Tracker API built with Django REST Framework and cookie-based JWT authentication.

## Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run all tests
python manage.py test

# Run tests with verbosity
python manage.py test -v 2

# Run a single test
python manage.py test app.tests.TestClassName.test_method_name
```

## Architecture

- **simplejwt/** - Django project configuration
  - `settings.py` - JWT with cookie support, DRF, drf-spectacular, django-filter
  - `urls.py` - Root URL routing with docs endpoints
- **app/** - Task tracker application
  - `models.py` - Task model with status, priority, due_date fields
  - `views.py` - Auth views (Login, Logout, Refresh) + TaskViewSet
  - `serializers.py` - Email login, Task, and User serializers
  - `authentication.py` - CookieJWTAuthentication class
  - `permissions.py` - IsTaskOwner custom permission
  - `filters.py` - TaskFilter for filtering by status, priority, due_date
  - `admin.py` - Admin configuration for Task model
  - `tests.py` - Comprehensive test suite (33 tests)

## API Endpoints

### Authentication (Cookie-based JWT with Email Login)
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login with email & password (sets cookies)
- `POST /api/auth/logout/` - Logout (clears cookies, blacklists token)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/verify/` - Verify token validity
- `GET /api/auth/me/` - Get current user profile

### Tasks
All task endpoints require authentication (via cookies or Bearer token).

- `GET /api/tasks/` - List tasks (supports filtering, search, ordering)
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `PATCH /api/tasks/{id}/` - Partial update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/tasks/stats/` - Get task statistics
- `POST /api/tasks/{id}/complete/` - Mark task as complete

### Documentation
- `GET /docs/` - Scalar interactive API documentation
- `GET /api/schema/` - OpenAPI schema (JSON)
- `GET /api/docs/swagger/` - Swagger UI
- `GET /api/docs/redoc/` - ReDoc

## Authentication

### Cookie-based (Browser)
1. Login at `/api/auth/login/` with email & password
2. Cookies (`access_token`, `refresh_token`) are set automatically
3. Subsequent requests use cookies automatically
4. Logout at `/api/auth/logout/` to clear cookies

### Bearer Token (API Clients)
Include header: `Authorization: Bearer <access_token>`

## Query Parameters

### Filtering
- `status` - Filter by status (todo, in_progress, done)
- `priority` - Filter by priority (low, medium, high)
- `due_date` - Exact due date
- `due_date_before` - Due on or before date
- `due_date_after` - Due on or after date
- `is_overdue` - Filter overdue tasks (true/false)

### Search
- `search` - Search in title and description

### Ordering
- `ordering` - Order by: created_at, due_date, priority, status
- Prefix with `-` for descending (e.g., `-created_at`)
