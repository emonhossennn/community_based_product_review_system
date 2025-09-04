"""
Simple pytest configuration without factory-boy
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

@pytest.fixture
def api_client():
    """Provides an API client for testing"""
    return APIClient()

@pytest.fixture
def user():
    """Creates a regular user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user():
    """Creates an admin user"""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Provides an authenticated API client"""
    token, created = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """Provides an admin authenticated API client"""
    token, created = Token.objects.get_or_create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client