# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Task Tracker API built with Django REST Framework and JWT authentication.

- use context7 for fetching every documentation

## Commands

```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Run a single test
python manage.py test app.tests.TestClassName.test_method_name
```

## Architecture

- **simplejwt/** - Django project configuration
  - `settings.py` - Configured with `JWTAuthentication` as default auth class
  - `urls.py` - Root URL routing with JWT token endpoints
- **app/** - Task tracker application with models, views, and serializers

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token pair (access + refresh)
- `POST /api/token/refresh/` - Refresh access token

### Tasks
All task endpoints require authentication via `Authorization: Bearer <token>` header.

## Authentication Flow

1. Obtain tokens via `/api/token/` with username/password
2. Include access token in requests: `Authorization: Bearer <token>`
3. Refresh expired access tokens via `/api/token/refresh/`
