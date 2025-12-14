# Task Tracker API

A production-ready RESTful API for managing tasks with JWT authentication stored in HTTP-only cookies, built with Django REST Framework.

## Features

- **Cookie-based JWT Authentication**: Secure HTTP-only cookies for token storage (XSS protection)
- **Email Login**: Login using email and password
- **User Registration**: Create new accounts with validated passwords
- **Task Management**: Full CRUD operations for personal tasks
- **Task Privacy**: Each user can only access their own tasks
- **Filtering**: Filter tasks by status, priority, due date, and overdue status
- **Search**: Search tasks by title and description
- **Ordering**: Sort tasks by creation date, due date, priority, or status
- **Pagination**: Paginated responses for efficient data loading
- **API Documentation**: Interactive Scalar-powered API documentation
- **Statistics**: Get task statistics by status and priority

## Tech Stack

- **Django 5.x**: Web framework
- **Django REST Framework**: API toolkit
- **djangorestframework-simplejwt**: JWT authentication with cookie support
- **drf-spectacular**: OpenAPI 3 schema generation
- **django-filter**: Advanced filtering
- **SQLite**: Database (easily switchable to PostgreSQL)

## Project Structure

```
dj-jwt/
├── simplejwt/              # Django project configuration
│   ├── settings.py         # Project settings with cookie JWT config
│   ├── urls.py             # Root URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── app/                    # Task tracker application
│   ├── models.py           # Task model
│   ├── views.py            # ViewSets and auth views
│   ├── serializers.py      # DRF serializers
│   ├── permissions.py      # Custom permissions
│   ├── filters.py          # Task filters
│   ├── authentication.py   # Cookie-based JWT authentication
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # App URL patterns
│   └── tests.py            # Test suite (33 tests)
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dj-jwt
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API: http://localhost:8000/api/
   - Documentation: http://localhost:8000/docs/
   - Admin: http://localhost:8000/admin/

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login with email & password |
| POST | `/api/auth/logout/` | Logout and clear cookies |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/verify/` | Verify token validity |
| GET | `/api/auth/me/` | Get current user profile |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List all tasks |
| POST | `/api/tasks/` | Create new task |
| GET | `/api/tasks/{id}/` | Get task details |
| PUT | `/api/tasks/{id}/` | Update task |
| PATCH | `/api/tasks/{id}/` | Partial update task |
| DELETE | `/api/tasks/{id}/` | Delete task |
| GET | `/api/tasks/stats/` | Get task statistics |
| POST | `/api/tasks/{id}/complete/` | Mark task as complete |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/docs/` | Scalar interactive docs |
| GET | `/api/schema/` | OpenAPI schema (JSON) |
| GET | `/api/docs/swagger/` | Swagger UI |
| GET | `/api/docs/redoc/` | ReDoc |

## Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "date_joined": "2025-01-15T10:30:00Z"
}
```

### Login with Email

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "date_joined": "2025-01-15T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Cookies set:**
- `access_token` (HTTP-only, 30 min)
- `refresh_token` (HTTP-only, 7 days)

### Create a Task (Using Cookies)

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "priority": "high",
    "due_date": "2025-02-01"
  }'
```

### Create a Task (Using Bearer Token)

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "priority": "high",
    "due_date": "2025-02-01"
  }'
```

### List Tasks with Filtering

```bash
# Filter by status
curl -X GET "http://localhost:8000/api/tasks/?status=todo" \
  -b cookies.txt

# Filter by priority
curl -X GET "http://localhost:8000/api/tasks/?priority=high" \
  -b cookies.txt

# Search by title/description
curl -X GET "http://localhost:8000/api/tasks/?search=documentation" \
  -b cookies.txt

# Order by due date
curl -X GET "http://localhost:8000/api/tasks/?ordering=due_date" \
  -b cookies.txt

# Filter overdue tasks
curl -X GET "http://localhost:8000/api/tasks/?is_overdue=true" \
  -b cookies.txt
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -b cookies.txt \
  -c cookies.txt
```

### Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -b cookies.txt
```

### Get Task Statistics

```bash
curl -X GET http://localhost:8000/api/tasks/stats/ \
  -b cookies.txt
```

**Response:**
```json
{
  "total": 10,
  "by_status": {
    "todo": 5,
    "in_progress": 3,
    "done": 2
  },
  "by_priority": {
    "low": 2,
    "medium": 5,
    "high": 3
  },
  "overdue": 1
}
```

## Task Model

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Auto-generated primary key |
| title | String | Task title (required, max 255 chars) |
| description | Text | Task description (optional) |
| status | Choice | todo, in_progress, done (default: todo) |
| priority | Choice | low, medium, high (default: medium) |
| due_date | Date | Due date (optional) |
| created_at | DateTime | Auto-set on creation |
| updated_at | DateTime | Auto-updated on save |
| user | ForeignKey | Owner of the task |

## Authentication

### Cookie-based Authentication (Recommended for Browsers)

The API uses HTTP-only cookies for secure token storage:

1. **Login** at `/api/auth/login/` with email and password
2. Cookies are automatically set:
   - `access_token`: Short-lived access token (30 min)
   - `refresh_token`: Long-lived refresh token (7 days)
3. Include cookies in subsequent requests (automatic in browsers)
4. **Refresh** tokens at `/api/auth/refresh/` before access token expires
5. **Logout** at `/api/auth/logout/` to clear cookies and blacklist tokens

### Bearer Token Authentication (For API Clients)

For non-browser clients, use the Authorization header:

```
Authorization: Bearer <access_token>
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test app.tests.TaskAPITests

# Run specific test method
python manage.py test app.tests.TaskAPITests.test_create_task

# Run with verbosity
python manage.py test -v 2
```

## Configuration

### Cookie Settings (in settings.py)

```python
SIMPLE_JWT = {
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    'AUTH_COOKIE_SECURE': True,       # HTTPS only in production
    'AUTH_COOKIE_HTTP_ONLY': True,    # XSS protection
    'AUTH_COOKIE_SAMESITE': 'Lax',    # CSRF protection
}
```

### Token Lifetimes

- Access Token: 30 minutes
- Refresh Token: 7 days

### Pagination

Default page size: 10 items per page

## API Documentation

Visit `/docs/` for interactive API documentation powered by Scalar. This provides:
- Complete endpoint documentation
- Request/response examples
- Authentication testing
- Code snippets in multiple languages

Alternative documentation:
- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- Raw OpenAPI Schema: `/api/schema/`

## Security Features

- **HTTP-only Cookies**: Tokens stored in HTTP-only cookies prevent XSS attacks
- **Short-lived Access Tokens**: 30 minute lifetime limits exposure
- **Token Rotation**: Refresh tokens are rotated on use
- **Token Blacklisting**: Logout invalidates refresh tokens
- **SameSite Cookies**: Protection against CSRF attacks
- **User Isolation**: Users can only access their own tasks
- **Password Validation**: Django's built-in password validators

## Production Deployment

1. Set `DEBUG=False`
2. Configure a proper `SECRET_KEY`
3. Switch to PostgreSQL
4. Set up HTTPS (required for secure cookies)
5. Configure `ALLOWED_HOSTS`
6. Set `AUTH_COOKIE_SECURE=True`
7. Use environment variables for sensitive data
8. Set up proper CORS settings

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Kunal Singh Dadhwal - 2025

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
