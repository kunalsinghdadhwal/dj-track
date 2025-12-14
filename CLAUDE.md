# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Task Tracker API built with Django REST Framework and JWT authentication.

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
  - `settings.py` - Configured with JWT, DRF, drf-spectacular, django-filter
  - `urls.py` - Root URL routing with JWT endpoints, docs, and app routes
- **app/** - Task tracker application
  - `models.py` - Task model with status, priority, due_date fields
  - `views.py` - TaskViewSet and UserRegistrationView
  - `serializers.py` - Task and User serializers
  - `permissions.py` - IsTaskOwner custom permission
  - `filters.py` - TaskFilter for filtering by status, priority, due_date
  - `admin.py` - Admin configuration for Task model
  - `tests.py` - Comprehensive test suite (29 tests)

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token pair (access + refresh)
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity

### Users
- `POST /api/register/` - Register new user
- `GET /api/profile/` - Get current user profile

### Tasks
All task endpoints require authentication via `Authorization: Bearer <token>` header.

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

## Authentication Flow

1. Register user via `POST /api/register/`
2. Obtain tokens via `POST /api/token/` with username/password
3. Include access token in requests: `Authorization: Bearer <token>`
4. Refresh expired access tokens via `POST /api/token/refresh/`
