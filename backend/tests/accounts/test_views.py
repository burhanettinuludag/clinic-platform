"""
Integration tests for accounts API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestRegisterView:
    """Tests for user registration endpoint."""

    def test_register_patient_success(self, api_client):
        """Test successful patient registration."""
        data = {
            'email': 'newpatient@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == 'newpatient@example.com'

    def test_register_with_mismatched_passwords(self, api_client):
        """Test registration fails with mismatched passwords."""
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_with_existing_email(self, api_client, patient_user):
        """Test registration fails with existing email."""
        data = {
            'email': patient_user.email,
            'password': 'password123',
            'password_confirm': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_with_short_password(self, api_client):
        """Test registration fails with short password."""
        data = {
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:
    """Tests for user login endpoint."""

    def test_login_success(self, api_client, user_factory):
        """Test successful login."""
        password = 'testpass123'
        user = user_factory(email='login@example.com', password=password)

        data = {
            'email': user.email,
            'password': password,
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_login_with_invalid_credentials(self, api_client, patient_user):
        """Test login fails with invalid credentials."""
        data = {
            'email': patient_user.email,
            'password': 'wrongpassword',
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_nonexistent_user(self, api_client):
        """Test login fails with non-existent user."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword',
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    """Tests for user logout endpoint."""

    def test_logout_success(self, authenticated_client, patient_user):
        """Test successful logout."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(patient_user)

        response = authenticated_client.post(
            '/api/v1/auth/logout/',
            {'refresh': str(refresh)}
        )
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_without_auth(self, api_client):
        """Test logout fails without authentication."""
        response = api_client.post('/api/v1/auth/logout/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfileView:
    """Tests for user profile endpoint."""

    def test_get_profile(self, authenticated_client, patient_user):
        """Test getting user profile."""
        response = authenticated_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == patient_user.email
        assert response.data['role'] == 'patient'

    def test_update_profile(self, authenticated_client):
        """Test updating user profile."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+901234567890',
        }
        response = authenticated_client.patch('/api/v1/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'

    def test_get_profile_without_auth(self, api_client):
        """Test getting profile fails without authentication."""
        response = api_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestChangePasswordView:
    """Tests for change password endpoint."""

    def test_change_password_success(self, api_client, user_factory):
        """Test successful password change."""
        old_password = 'oldpass123'
        new_password = 'newpass456'
        user = user_factory(email='pwchange@example.com', password=old_password)

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {
            'old_password': old_password,
            'new_password': new_password,
        }
        response = api_client.post('/api/v1/auth/change-password/', data)
        assert response.status_code == status.HTTP_200_OK

        # Verify new password works
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change fails with wrong old password."""
        data = {
            'old_password': 'wrongoldpass',
            'new_password': 'newpass456',
        }
        response = authenticated_client.post('/api/v1/auth/change-password/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
