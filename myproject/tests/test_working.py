"""
Working API Tests with Allure reporting
"""
import pytest
import allure
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from myproject.models import Product, Comment

@allure.epic("Product Review System")
@allure.feature("API Testing")
class TestProductAPI(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product for API testing"
        )
    
    @allure.story("Product Listing")
    @allure.title("Get all products")
    @allure.description("Test that anyone can view the list of products")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_products(self):
        """Test getting all products"""
        with allure.step("Make GET request to products endpoint"):
            response = self.client.get('/api/products/')
        
        with allure.step("Verify response status and data"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) >= 1
            # Find our test product in the response
            product_names = [p['name'] for p in response.data]
            assert "Test Product" in product_names
        
        allure.attach(
            str(response.data),
            name="Products Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("Product Details")
    @allure.title("Get specific product")
    @allure.description("Test retrieving details of a specific product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_detail(self):
        """Test getting specific product details"""
        with allure.step("Request product details"):
            response = self.client.get(f'/api/products/{self.product.id}/')
        
        with allure.step("Verify product details"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data['name'] == "Test Product"
            assert response.data['description'] == "A test product for API testing"
    
    @allure.story("Authentication")
    @allure.title("Comment creation requires authentication")
    @allure.description("Test that creating comments requires authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_comment_requires_auth(self):
        """Test that creating comments requires authentication"""
        with allure.step("Attempt to create comment without authentication"):
            comment_data = {
                'product': self.product.id,
                'content': 'This should fail without auth'
            }
            response = self.client.post('/api/comments/', comment_data)
        
        with allure.step("Verify authentication is required"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @allure.story("Product Comments")
    @allure.title("Get product comments")
    @allure.description("Test getting comments for a specific product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_comments(self):
        """Test getting comments for a product"""
        with allure.step("Request product comments"):
            response = self.client.get(f'/api/products/{self.product.id}/comments/')
        
        with allure.step("Verify response"):
            assert response.status_code == status.HTTP_200_OK
            # Should return empty list initially (no approved comments)
            assert isinstance(response.data, list)

@allure.epic("Product Review System")
@allure.feature("Data Models")
class TestModels(TestCase):
    
    @allure.story("Model Creation")
    @allure.title("Create product model")
    @allure.description("Test creating a product model instance")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_product(self):
        """Test creating a product"""
        with allure.step("Create product instance"):
            product = Product.objects.create(
                name="iPhone 16",
                description="Latest iPhone model"
            )
        
        with allure.step("Verify product attributes"):
            assert product.name == "iPhone 16"
            assert product.description == "Latest iPhone model"
            assert product.id is not None
    
    @allure.story("Model Creation")
    @allure.title("Create comment model")
    @allure.description("Test creating a comment model instance")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_comment(self):
        """Test creating a comment"""
        with allure.step("Create user and product"):
            user = User.objects.create_user('testuser', 'test@example.com', 'pass')
            product = Product.objects.create(name="Test Product")
        
        with allure.step("Create comment"):
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Great product!"
            )
        
        with allure.step("Verify comment attributes"):
            assert comment.content == "Great product!"
            assert comment.user == user
            assert comment.product == product
            assert comment.is_approved == False  # Default should be False