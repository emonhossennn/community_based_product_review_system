"""
Comment API Tests with Allure reporting
"""
import pytest
import allure
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from myproject.models import Product, Comment

@allure.epic("Product Review System")
@allure.feature("Comment Management")
class TestCommentAPI(APITestCase):
    
    @allure.story("Comment Creation")
    @allure.title("Create comment with authentication")
    @allure.description("Test that authenticated users can create comments")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_comment_authenticated(self):
        """Test creating a comment with authentication"""
        with allure.step("Create user and authenticate"):
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
            token, created = Token.objects.get_or_create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        with allure.step("Create a product"):
            product = Product.objects.create(name="Test Product")
        
        with allure.step("Prepare comment data"):
            comment_data = {
                'product': product.id,
                'content': 'This is a great product!'
            }
        
        with allure.step("Create comment via API"):
            url = '/api/comments/'
            response = self.client.post(url, comment_data, format='json')
        
        with allure.step("Verify comment creation"):
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['content'] == 'This is a great product!'
            assert response.data['user'] == user.id
            assert response.data['is_approved'] == False  # Should be pending approval
        
        allure.attach(
            str(response.data),
            name="Created Comment",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("Authentication")
    @allure.title("Reject comment creation without authentication")
    @allure.description("Test that unauthenticated users cannot create comments")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_comment_unauthenticated(self, api_client):
        """Test creating a comment without authentication fails"""
        with allure.step("Create a product"):
            product = Product.objects.create(name="Test Product")
        
        with allure.step("Attempt to create comment without auth"):
            comment_data = {
                'product': product.id,
                'content': 'This should fail!'
            }
            url = reverse('comment-list')
            response = api_client.post(url, comment_data, format='json')
        
        with allure.step("Verify authentication required"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @allure.story("Comment Listing")
    @allure.title("User can view their own comments")
    @allure.description("Test that users can view their own comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_user_comments(self, authenticated_client, user):
        """Test listing user's own comments"""
        with allure.step("Create product and comment"):
            product = Product.objects.create(name="Test Product")
            Comment.objects.create(
                product=product,
                user=user,
                content="My comment"
            )
        
        with allure.step("Get user's comments"):
            url = reverse('comment-list')
            response = authenticated_client.get(url)
        
        with allure.step("Verify user can see their comments"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == "My comment"
    
    @allure.story("Comment Updates")
    @allure.title("Update own comment")
    @allure.description("Test that users can update their own comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_own_comment(self, authenticated_client, user):
        """Test updating user's own comment"""
        with allure.step("Create product and comment"):
            product = Product.objects.create(name="Test Product")
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Original comment"
            )
        
        with allure.step("Update comment"):
            url = reverse('comment-detail', kwargs={'pk': comment.id})
            update_data = {'content': 'Updated comment'}
            response = authenticated_client.patch(url, update_data, format='json')
        
        with allure.step("Verify comment updated"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data['content'] == 'Updated comment'
    
    @allure.story("Comment Deletion")
    @allure.title("Delete own comment")
    @allure.description("Test that users can delete their own comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_own_comment(self, authenticated_client, user):
        """Test deleting user's own comment"""
        with allure.step("Create product and comment"):
            product = Product.objects.create(name="Test Product")
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Comment to delete"
            )
        
        with allure.step("Delete comment"):
            url = reverse('comment-detail', kwargs={'pk': comment.id})
            response = authenticated_client.delete(url)
        
        with allure.step("Verify comment deleted"):
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert not Comment.objects.filter(id=comment.id).exists()

@allure.epic("Product Review System")
@allure.feature("Admin Comment Management")
class TestAdminCommentAPI:
    
    @allure.story("Comment Approval")
    @allure.title("Admin can approve comments")
    @allure.description("Test that admin users can approve pending comments")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_admin_approve_comment(self, admin_client, user):
        """Test admin approving a comment"""
        with allure.step("Create product and pending comment"):
            product = Product.objects.create(name="Test Product")
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Pending comment",
                is_approved=False
            )
        
        with allure.step("Admin approves comment"):
            url = reverse('comment-approve', kwargs={'pk': comment.id})
            response = admin_client.patch(url)
        
        with allure.step("Verify comment approved"):
            assert response.status_code == status.HTTP_200_OK
            comment.refresh_from_db()
            assert comment.is_approved == True
    
    @allure.story("Comment Rejection")
    @allure.title("Admin can reject comments")
    @allure.description("Test that admin users can reject comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_reject_comment(self, admin_client, user):
        """Test admin rejecting a comment"""
        with allure.step("Create product and comment"):
            product = Product.objects.create(name="Test Product")
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Comment to reject",
                is_approved=False
            )
        
        with allure.step("Admin rejects comment"):
            url = reverse('comment-reject', kwargs={'pk': comment.id})
            response = admin_client.patch(url)
        
        with allure.step("Verify comment still not approved"):
            assert response.status_code == status.HTTP_200_OK
            comment.refresh_from_db()
            assert comment.is_approved == False
    
    @allure.story("Admin Views")
    @allure.title("Admin can view pending comments")
    @allure.description("Test that admin can view all pending comments")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_view_pending_comments(self, admin_client, user):
        """Test admin viewing pending comments"""
        with allure.step("Create products and comments"):
            product = Product.objects.create(name="Test Product")
            Comment.objects.create(
                product=product,
                user=user,
                content="Pending comment 1",
                is_approved=False
            )
            Comment.objects.create(
                product=product,
                user=user,
                content="Approved comment",
                is_approved=True
            )
        
        with allure.step("Get pending comments"):
            url = reverse('comment-pending')
            response = admin_client.get(url)
        
        with allure.step("Verify only pending comments returned"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == "Pending comment 1"
    
    @allure.story("Authorization")
    @allure.title("Regular user cannot access admin endpoints")
    @allure.description("Test that regular users cannot access admin-only endpoints")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_regular_user_cannot_approve(self, authenticated_client, user):
        """Test regular user cannot approve comments"""
        with allure.step("Create product and comment"):
            product = Product.objects.create(name="Test Product")
            comment = Comment.objects.create(
                product=product,
                user=user,
                content="Comment",
                is_approved=False
            )
        
        with allure.step("Regular user tries to approve"):
            url = reverse('comment-approve', kwargs={'pk': comment.id})
            response = authenticated_client.patch(url)
        
        with allure.step("Verify access denied"):
            assert response.status_code == status.HTTP_403_FORBIDDEN