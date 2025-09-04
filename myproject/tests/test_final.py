"""
Final Working API Tests for SQA Portfolio
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from myproject.models import Product, Comment

class TestSQAPortfolio(APITestCase):
    """Professional SQA test suite demonstrating comprehensive API testing"""
    
    def setUp(self):
        """Set up test data for each test"""
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
            name="iPhone 16 Pro",
            description="Latest flagship smartphone with advanced camera"
        )
    
    def test_01_public_product_access(self):
        """Test that products are publicly accessible without authentication"""
        response = self.client.get('/api/products/')
        
        # Verify successful response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Verify product data structure
        if len(response.data) > 0:
            product_data = response.data[0]
            self.assertIn('name', product_data)
            self.assertIn('description', product_data)
            self.assertIn('id', product_data)
    
    def test_02_product_detail_retrieval(self):
        """Test retrieving specific product details"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        
        # Verify successful response and correct data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "iPhone 16 Pro")
        self.assertEqual(response.data['description'], "Latest flagship smartphone with advanced camera")
    
    def test_03_authentication_required_for_comments(self):
        """Test that comment creation requires authentication"""
        comment_data = {
            'product': self.product.id,
            'content': 'This should fail without authentication!'
        }
        response = self.client.post('/api/comments/', comment_data)
        
        # Verify authentication is required
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_04_authenticated_comment_creation(self):
        """Test successful comment creation with proper authentication"""
        # Authenticate user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Create comment
        comment_data = {
            'product': self.product.id,
            'content': 'Excellent camera quality and performance!'
        }
        response = self.client.post('/api/comments/', comment_data)
        
        # Verify successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Excellent camera quality and performance!')
        self.assertEqual(response.data['user'], self.user.id)
        
        # Verify comment is pending approval by default
        comment = Comment.objects.get(id=response.data['id'])
        self.assertFalse(comment.is_approved)
    
    def test_05_admin_comment_approval_workflow(self):
        """Test admin approval workflow for comments"""
        # Create a pending comment
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Great product, highly recommended!",
            is_approved=False
        )
        
        # Authenticate as admin
        admin_token, created = Token.objects.get_or_create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        # Approve the comment
        response = self.client.patch(f'/api/comments/{comment.id}/approve/')
        
        # Verify successful approval
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify comment is now approved in database
        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)
    
    def test_06_public_approved_comments_only(self):
        """Test that only approved comments are visible to public"""
        # Create both approved and unapproved comments
        approved_comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="This is an approved comment",
            is_approved=True
        )
        unapproved_comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="This is an unapproved comment",
            is_approved=False
        )
        
        # Get public comments for the product
        response = self.client.get(f'/api/products/{self.product.id}/comments/')
        
        # Verify only approved comments are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "This is an approved comment")
    
    def test_07_user_comment_isolation(self):
        """Test that users can only access their own comments"""
        # Create another user and comments for both users
        other_user = User.objects.create_user('otheruser', 'other@test.com', 'pass')
        
        user_comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="My personal comment"
        )
        other_comment = Comment.objects.create(
            product=self.product,
            user=other_user,
            content="Other user's comment"
        )
        
        # Authenticate as first user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Get user's comments
        response = self.client.get('/api/comments/')
        
        # Verify user only sees their own comments
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_comment_contents = [comment['content'] for comment in response.data]
        self.assertIn("My personal comment", user_comment_contents)
        self.assertNotIn("Other user's comment", user_comment_contents)
    
    def test_08_authorization_admin_only_functions(self):
        """Test that regular users cannot access admin-only functions"""
        # Create a comment
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Test comment for authorization",
            is_approved=False
        )
        
        # Authenticate as regular user (not admin)
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Try to approve comment (should fail)
        response = self.client.patch(f'/api/comments/{comment.id}/approve/')
        
        # Verify access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_09_admin_pending_comments_view(self):
        """Test admin can view all pending comments"""
        # Create multiple comments with different approval states
        Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Pending comment 1",
            is_approved=False
        )
        Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Approved comment",
            is_approved=True
        )
        Comment.objects.create(
            product=self.product,
            user=self.user,
            content="Pending comment 2",
            is_approved=False
        )
        
        # Authenticate as admin
        admin_token, created = Token.objects.get_or_create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        # Get pending comments
        response = self.client.get('/api/comments/pending/')
        
        # Verify only pending comments are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify all returned comments are pending
        for comment in response.data:
            self.assertFalse(comment['is_approved'])
    
    def test_10_error_handling_nonexistent_resources(self):
        """Test proper error handling for non-existent resources"""
        # Test non-existent product
        response = self.client.get('/api/products/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test non-existent product comments
        response = self.client.get('/api/products/99999/comments/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_11_data_validation_comment_creation(self):
        """Test data validation for comment creation"""
        # Authenticate user
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Test empty content
        response = self.client.post('/api/comments/', {
            'product': self.product.id,
            'content': ''
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing product
        response = self.client.post('/api/comments/', {
            'content': 'Comment without product'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid product ID
        response = self.client.post('/api/comments/', {
            'product': 99999,
            'content': 'Comment for non-existent product'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)