# Task Tracker API

A production-ready RESTful API for managing tasks with JWT authentication, built with Django REST Framework.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
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
- **djangorestframework-simplejwt**: JWT authentication
- **drf-spectacular**: OpenAPI 3 schema generation
- **django-filter**: Advanced filtering
- **SQLite**: Database (easily switchable to PostgreSQL)

## Project Structure

```
dj-jwt/
├── simplejwt/              # Django project configuration
│   ├── settings.py         # Project settings
│   ├── urls.py             # Root URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── app/                    # Task tracker application
│   ├── models.py           # Task model
│   ├── views.py            # ViewSets and API views
│   ├── serializers.py      # DRF serializers
│   ├── permissions.py      # Custom permissions
│   ├── filters.py          # Task filters
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # App URL patterns
│   └── tests.py            # Test suite
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
| POST | `/api/token/` | Obtain JWT token pair |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/token/verify/` | Verify token validity |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register new user |
| GET | `/api/profile/` | Get current user profile |

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
curl -X POST http://localhost:8000/api/register/ \
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

### Obtain JWT Tokens

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Create a Task

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

**Response:**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "todo",
  "priority": "high",
  "due_date": "2025-02-01",
  "created_at": "2025-01-15T10:35:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

### List Tasks with Filtering

```bash
# Filter by status
curl -X GET "http://localhost:8000/api/tasks/?status=todo" \
  -H "Authorization: Bearer <your_access_token>"

# Filter by priority
curl -X GET "http://localhost:8000/api/tasks/?priority=high" \
  -H "Authorization: Bearer <your_access_token>"

# Search by title/description
curl -X GET "http://localhost:8000/api/tasks/?search=documentation" \
  -H "Authorization: Bearer <your_access_token>"

# Order by due date
curl -X GET "http://localhost:8000/api/tasks/?ordering=due_date" \
  -H "Authorization: Bearer <your_access_token>"

# Filter overdue tasks
curl -X GET "http://localhost:8000/api/tasks/?is_overdue=true" \
  -H "Authorization: Bearer <your_access_token>"
```

### Update a Task

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "status": "in_progress"
  }'
```

### Mark Task as Complete

```bash
curl -X POST http://localhost:8000/api/tasks/1/complete/ \
  -H "Authorization: Bearer <your_access_token>"
```

### Get Task Statistics

```bash
curl -X GET http://localhost:8000/api/tasks/stats/ \
  -H "Authorization: Bearer <your_access_token>"
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

### Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
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

### Environment Variables (Production)

For production, set these environment variables:

```bash
SECRET_KEY=your-super-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@localhost:5432/tasktracker
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

### JWT Token Settings

Default token lifetimes (configurable in `settings.py`):
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

## Security Considerations

- JWT tokens are short-lived (30 min access, 7 days refresh)
- Refresh token rotation is enabled
- All task endpoints require authentication
- Users can only access their own tasks
- Passwords are validated against Django's password validators
- CORS is configured for development (restrict in production)

## Production Deployment

1. Set `DEBUG=False`
2. Configure a proper `SECRET_KEY`
3. Switch to PostgreSQL
4. Set up HTTPS
5. Configure `ALLOWED_HOSTS`
6. Use environment variables for sensitive data
7. Set up proper CORS settings

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
