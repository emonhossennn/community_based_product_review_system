"""
Simple tests to verify setup
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from myproject.models import Product, Comment

class TestBasicSetup(TestCase):
    """Basic tests to verify Django setup"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
    
    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(name='Test Product', description='Test Description')
        assert product.name == 'Test Product'
        assert product.description == 'Test Description'
    
    def test_create_comment(self):
        """Test creating a comment"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        product = Product.objects.create(name='Test Product')
        comment = Comment.objects.create(
            product=product,
            user=user,
            content='Test comment'
        )
        assert comment.content == 'Test comment'
        assert comment.user == user
        assert comment.product == product
        assert comment.is_approved == False  # Default should be False