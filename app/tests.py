"""
Task Tracker API Tests

Comprehensive test suite for the Task Tracker API including:
- User registration
- Cookie-based JWT authentication with email login
- Task CRUD operations
- Filtering, searching, and ordering
- Permission checks
"""

from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Task


class TaskModelTests(TestCase):
    """Tests for the Task model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_task(self):
        """Test creating a task."""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, Task.Status.TODO)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertEqual(task.user, self.user)

    def test_task_str_representation(self):
        """Test task string representation."""
        task = Task.objects.create(
            title='Test Task',
            user=self.user
        )
        self.assertIn('Test Task', str(task))

    def test_task_is_overdue(self):
        """Test is_overdue property."""
        # Task with past due date
        overdue_task = Task.objects.create(
            title='Overdue Task',
            due_date=date.today() - timedelta(days=1),
            user=self.user
        )
        self.assertTrue(overdue_task.is_overdue)

        # Task with future due date
        future_task = Task.objects.create(
            title='Future Task',
            due_date=date.today() + timedelta(days=1),
            user=self.user
        )
        self.assertFalse(future_task.is_overdue)

        # Completed task (should not be overdue)
        done_task = Task.objects.create(
            title='Done Task',
            due_date=date.today() - timedelta(days=1),
            status=Task.Status.DONE,
            user=self.user
        )
        self.assertFalse(done_task.is_overdue)


class UserRegistrationTests(APITestCase):
    """Tests for user registration."""

    def test_register_user_success(self):
        """Test successful user registration."""
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords."""
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        url = reverse('auth-register')
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailLoginTests(APITestCase):
    """Tests for email-based login with cookies."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful login with email."""
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['message'], 'Login successful')

        # Check cookies are set
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        url = reverse('auth-login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_password(self):
        """Test login with wrong password."""
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test logout clears cookies."""
        # First login
        login_url = reverse('auth-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Then logout
        logout_url = reverse('auth-logout')
        logout_response = self.client.post(logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(logout_response.data['message'], 'Logout successful')

    def test_token_refresh(self):
        """Test refreshing access token."""
        # First login
        login_url = reverse('auth-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Refresh token
        refresh_url = reverse('auth-refresh')
        refresh_response = self.client.post(refresh_url, {'refresh': refresh_token})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_token_verify(self):
        """Test verifying access token."""
        # First login to set cookies
        login_url = reverse('auth-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data)
        access_token = login_response.data['access']

        # Set the cookie for verification
        self.client.cookies['access_token'] = access_token

        # Verify token
        verify_url = reverse('auth-verify')
        verify_response = self.client.get(verify_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data['valid'])


class CookieAuthenticationTests(APITestCase):
    """Tests for cookie-based authentication."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()

    def test_access_with_cookie(self):
        """Test accessing protected endpoint with cookie."""
        # Login to get token
        login_url = reverse('auth-login')
        login_response = self.client.post(login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        access_token = login_response.data['access']

        # Set cookie and access protected endpoint
        self.client.cookies['access_token'] = access_token

        profile_url = reverse('auth-me')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_access_with_bearer_token(self):
        """Test that Bearer token still works as fallback."""
        # Login to get token
        login_url = reverse('auth-login')
        login_response = self.client.post(login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        access_token = login_response.data['access']

        # Use Bearer token header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        profile_url = reverse('auth-me')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class TaskAPITests(APITestCase):
    """Tests for Task API endpoints."""

    def setUp(self):
        """Set up test data and authentication."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client = APIClient()

        # Login and get token
        login_url = reverse('auth-login')
        response = self.client.post(login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create some test tasks
        self.task1 = Task.objects.create(
            title='Task 1',
            description='Description 1',
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            user=self.user
        )
        self.task2 = Task.objects.create(
            title='Task 2',
            description='Description 2',
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.MEDIUM,
            user=self.user
        )
        self.other_task = Task.objects.create(
            title='Other Task',
            user=self.other_user
        )

    def test_list_tasks(self):
        """Test listing tasks."""
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own tasks (2)
        self.assertEqual(response.data['count'], 2)

    def test_create_task(self):
        """Test creating a task."""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'priority': 'high'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(user=self.user).count(), 3)

    def test_create_task_empty_title(self):
        """Test creating a task with empty title."""
        url = reverse('task-list')
        data = {
            'title': '   ',
            'description': 'Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_task(self):
        """Test retrieving a single task."""
        url = reverse('task-detail', args=[self.task1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Task 1')

    def test_retrieve_other_user_task(self):
        """Test that users cannot access other users' tasks."""
        url = reverse('task-detail', args=[self.other_task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        """Test updating a task."""
        url = reverse('task-detail', args=[self.task1.id])
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'status': 'in_progress',
            'priority': 'low'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Task')
        self.assertEqual(self.task1.status, Task.Status.IN_PROGRESS)

    def test_partial_update_task(self):
        """Test partially updating a task."""
        url = reverse('task-detail', args=[self.task1.id])
        data = {'status': 'done'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, Task.Status.DONE)

    def test_delete_task(self):
        """Test deleting a task."""
        url = reverse('task-detail', args=[self.task1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_delete_other_user_task(self):
        """Test that users cannot delete other users' tasks."""
        url = reverse('task-detail', args=[self.other_task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=self.other_task.id).exists())

    def test_filter_by_status(self):
        """Test filtering tasks by status."""
        url = reverse('task-list')
        response = self.client.get(url, {'status': 'todo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_priority(self):
        """Test filtering tasks by priority."""
        url = reverse('task-list')
        response = self.client.get(url, {'priority': 'high'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_tasks(self):
        """Test searching tasks."""
        url = reverse('task-list')
        response = self.client.get(url, {'search': 'Task 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_order_tasks(self):
        """Test ordering tasks."""
        url = reverse('task-list')
        response = self.client.get(url, {'ordering': 'priority'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_stats(self):
        """Test task statistics endpoint."""
        url = reverse('task-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
        self.assertIn('by_priority', response.data)
        self.assertEqual(response.data['total'], 2)

    def test_complete_task(self):
        """Test marking a task as complete."""
        url = reverse('task-complete', args=[self.task1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, Task.Status.DONE)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access tasks."""
        # Create a new client without any authentication
        unauthenticated_client = APIClient()
        url = reverse('task-list')
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(APITestCase):
    """Tests for user profile endpoint."""

    def setUp(self):
        """Set up test data and authentication."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()

        # Login and get token
        login_url = reverse('auth-login')
        response = self.client.post(login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_profile(self):
        """Test getting user profile."""
        url = reverse('auth-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_profile_unauthenticated(self):
        """Test that unauthenticated users cannot access profile."""
        # Create a new client without any authentication
        unauthenticated_client = APIClient()
        url = reverse('auth-me')
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
