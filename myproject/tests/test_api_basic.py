"""
API Tests with Allure reporting for your project
"""
import pytest
import allure
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from myproject.models import Product, Comment

@allure.epic("Product Review System")
@allure.feature("Basic API Testing")
class TestBasicAPI(APITestCase):
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product"
        )
    
    @allure.story("Product API")
    @allure.title("Get all products without authentication")
    @allure.description("Test that anyone can view products")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_products_public(self):
        """Test getting products without authentication"""
        with allure.step("Request products list"):
            response = self.client.get('/api/products/')
        
        with allure.step("Verify response"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) >= 1
            assert response.data[0]['name'] == "Test Product"
    
    @allure.story("Product API")
    @allure.title("Get product details")
    @allure.description("Test getting specific product details")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_detail(self):
        """Test getting product details"""
        with allure.step("Request product details"):
            response = self.client.get(f'/api/products/{self.product.id}/')
        
        with allure.step("Verify product data"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data['name'] == "Test Product"
            assert response.data['description'] == "A test product"
    
    @allure.story("Authentication")
    @allure.title("Create comment requires authentication")
    @allure.description("Test that creating comments requires authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_comment_requires_auth(self):
        """Test that creating comments requires authentication"""
        with allure.step("Attempt to create comment without auth"):
            comment_data = {
                'product': self.product.id,
                'content': 'This should fail!'
            }
            response = self.client.post('/api/comments/', comment_data)
        
        with allure.step("Verify authentication required"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @allure.story("Comment API")
    @allure.title("Create comment with authentication")
    @allure.description("Test creating a comment with proper authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_comment_authenticated(self):
        """Test creating a comment with authentication"""
        with allure.step("Authenticate user"):
            token, created = Token.objects.get_or_create(user=self.user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        with allure.step("Create comment"):
            comment_data = {
                'product': self.product.id,
                'content': 'Great product!'
            }
            response = self.client.post('/api/comments/', comment_data)
        
        with allure.step("Verify comment created"):
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['content'] == 'Great product!'
            assert response.data['is_approved'] == False
    
    @allure.story("Admin Functions")
    @allure.title("Admin can approve comments")
    @allure.description("Test that admin users can approve comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_approve_comment(self):
        """Test admin approving a comment"""
        with allure.step("Create a comment"):
            comment = Comment.objects.create(
                product=self.product,
                user=self.user,
                content="Test comment",
                is_approved=False
            )
        
        with allure.step("Authenticate as admin"):
            admin_token, created = Token.objects.get_or_create(user=self.admin_user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        with allure.step("Approve comment"):
            response = self.client.patch(f'/api/comments/{comment.id}/approve/')
        
        with allure.step("Verify comment approved"):
            assert response.status_code == status.HTTP_200_OK
            comment.refresh_from_db()
            assert comment.is_approved == True
    
    @allure.story("Product Comments")
    @allure.title("Get approved comments for product")
    @allure.description("Test getting only approved comments for a product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_comments(self):
        """Test getting approved comments for a product"""
        with allure.step("Create approved and unapproved comments"):
            Comment.objects.create(
                product=self.product,
                user=self.user,
                content="Approved comment",
                is_approved=True
            )
            Comment.objects.create(
                product=self.product,
                user=self.user,
                content="Unapproved comment",
                is_approved=False
            )
        
        with allure.step("Get product comments"):
            response = self.client.get(f'/api/products/{self.product.id}/comments/')
        
        with allure.step("Verify only approved comments returned"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == "Approved comment"