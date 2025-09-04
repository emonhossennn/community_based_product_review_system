"""
Clean API Tests without Allure (for basic testing)
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from myproject.models import Product, Comment

class TestBasicAPI(APITestCase):
    """Basic API tests without external dependencies"""
    
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
    
    def test_get_products_public(self):
        """Test getting products without authentication"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Product")
    
    def test_get_product_detail(self):
        """Test getting product details"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")
        self.assertEqual(response.data['description'], "A test product")
    
    def test_create_comment_requires_auth(self):
        """Test that creating comments requires authentication"""
        comment_data = {
            'product': self.product.id,
            'content': 'This should fail!'
        }
        response = self.client.post('/api/comments/', comment_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_comment_authenticated(self):
        """Test creating a comment with authentication"""
        # Authenticate user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Create comment
        comment_data = {
            'product': self.product.id,
            'content': 'Great product!'
        }
        response = self.client.post('/api/comments/', comment_data)
        
        # Verify comment created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Great product!')
        self.assertEqual(response.data['is_approved'], False)
    
    def test_admin_approve_comment(self):
        """Test admin approving a comment"""
        # Create a comment
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Test comment",
            is_approved=False
        )
        
        # Authenticate as admin
        admin_token, created = Token.objects.get_or_create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        # Approve comment
        response = self.client.patch(f'/api/comments/{comment.id}/approve/')
        
        # Verify comment approved
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)
    
    def test_get_product_comments(self):
        """Test getting approved comments for a product"""
        # Create approved and unapproved comments
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
        
        # Get product comments
        response = self.client.get(f'/api/products/{self.product.id}/comments/')
        
        # Verify only approved comments returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Approved comment")
    
    def test_user_can_only_see_own_comments(self):
        """Test that users can only see their own comments"""
        # Create another user
        other_user = User.objects.create_user('otheruser', 'other@test.com', 'pass')
        
        # Create comments for both users
        Comment.objects.create(
            product=self.product,
            user=self.user,
            content="My comment"
        )
        Comment.objects.create(
            product=self.product,
            user=other_user,
            content="Other user's comment"
        )
        
        # Authenticate as first user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Get comments
        response = self.client.get('/api/comments/')
        
        # Verify user only sees their own comment
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "My comment")
    
    def test_regular_user_cannot_approve_comments(self):
        """Test that regular users cannot approve comments"""
        # Create a comment
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Test comment",
            is_approved=False
        )
        
        # Authenticate as regular user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Try to approve comment
        response = self.client.patch(f'/api/comments/{comment.id}/approve/')
        
        # Verify access denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)