"""
Pytest configuration and fixtures for the Product Review System tests
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())

@pytest.fixture
def api_client():
    """Provides an API client for testing"""
    return APIClient()

@pytest.fixture
def user():
    """Creates a regular user"""
    return UserFactory()

@pytest.fixture
def admin_user():
    """Creates an admin user"""
    user = UserFactory(is_staff=True, is_superuser=True)
    return user

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