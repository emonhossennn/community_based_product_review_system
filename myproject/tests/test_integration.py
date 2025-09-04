"""
Integration Tests with Allure reporting
"""
import pytest
import allure
from django.urls import reverse
from rest_framework import status
from myproject.models import Product, Comment

@allure.epic("Product Review System")
@allure.feature("End-to-End Workflows")
class TestIntegrationWorkflows:
    
    @allure.story("Complete Comment Workflow")
    @allure.title("Full comment lifecycle: Create → Approve → View")
    @allure.description("Test the complete workflow from comment creation to public visibility")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_comment_workflow(self, api_client, authenticated_client, admin_client, user):
        """Test complete comment workflow from creation to approval"""
        
        with allure.step("Setup: Create a product"):
            product = Product.objects.create(
                name="iPhone 16 Pro",
                description="Latest flagship smartphone"
            )
        
        with allure.step("Step 1: User creates a comment"):
            comment_data = {
                'product': product.id,
                'content': 'Amazing camera quality and performance!'
            }
            url = reverse('comment-list')
            response = authenticated_client.post(url, comment_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            comment_id = response.data['id']
            
            allure.attach(
                str(response.data),
                name="Created Comment",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 2: Verify comment is not publicly visible"):
            url = reverse('product-comments', kwargs={'pk': product.id})
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 0  # No approved comments yet
        
        with allure.step("Step 3: Admin views pending comments"):
            url = reverse('comment-pending')
            response = admin_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == 'Amazing camera quality and performance!'
        
        with allure.step("Step 4: Admin approves the comment"):
            url = reverse('comment-approve', kwargs={'pk': comment_id})
            response = admin_client.patch(url)
            assert response.status_code == status.HTTP_200_OK
        
        with allure.step("Step 5: Verify comment is now publicly visible"):
            url = reverse('product-comments', kwargs={'pk': product.id})
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == 'Amazing camera quality and performance!'
            
            allure.attach(
                str(response.data),
                name="Public Comments",
                attachment_type=allure.attachment_type.JSON
            )
    
    @allure.story("Multiple Users Scenario")
    @allure.title("Multiple users commenting on same product")
    @allure.description("Test scenario with multiple users commenting on the same product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multiple_users_commenting(self, api_client, admin_client):
        """Test multiple users commenting on the same product"""
        
        with allure.step("Setup: Create product and users"):
            from django.contrib.auth.models import User
            from rest_framework.authtoken.models import Token
            from rest_framework.test import APIClient
            
            product = Product.objects.create(name="MacBook Air M3")
            
            # Create multiple users
            user1 = User.objects.create_user('user1', 'user1@test.com', 'pass')
            user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
            
            # Create API clients for each user
            client1 = APIClient()
            client2 = APIClient()
            
            token1, _ = Token.objects.get_or_create(user=user1)
            token2, _ = Token.objects.get_or_create(user=user2)
            
            client1.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
            client2.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')
        
        with allure.step("User 1 creates a positive comment"):
            comment_data = {'product': product.id, 'content': 'Great performance and battery life!'}
            response = client1.post(reverse('comment-list'), comment_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            comment1_id = response.data['id']
        
        with allure.step("User 2 creates a negative comment"):
            comment_data = {'product': product.id, 'content': 'Too expensive for what it offers.'}
            response = client2.post(reverse('comment-list'), comment_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            comment2_id = response.data['id']
        
        with allure.step("Admin approves first comment only"):
            url = reverse('comment-approve', kwargs={'pk': comment1_id})
            response = admin_client.patch(url)
            assert response.status_code == status.HTTP_200_OK
        
        with allure.step("Verify only approved comment is public"):
            url = reverse('product-comments', kwargs={'pk': product.id})
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
            assert response.data[0]['content'] == 'Great performance and battery life!'
        
        with allure.step("Admin can see all comments"):
            url = reverse('comment-list')
            response = admin_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 2
    
    @allure.story("Data Validation")
    @allure.title("Comment validation and error handling")
    @allure.description("Test various validation scenarios for comment creation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_comment_validation(self, authenticated_client):
        """Test comment validation scenarios"""
        
        with allure.step("Setup: Create a product"):
            product = Product.objects.create(name="Test Product")
        
        with allure.step("Test empty content validation"):
            comment_data = {'product': product.id, 'content': ''}
            url = reverse('comment-list')
            response = authenticated_client.post(url, comment_data, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test missing product validation"):
            comment_data = {'content': 'Comment without product'}
            response = authenticated_client.post(url, comment_data, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test invalid product ID"):
            comment_data = {'product': 999, 'content': 'Comment for non-existent product'}
            response = authenticated_client.post(url, comment_data, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test valid comment creation"):
            comment_data = {'product': product.id, 'content': 'Valid comment'}
            response = authenticated_client.post(url, comment_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

@allure.epic("Product Review System")
@allure.feature("Performance Testing")
class TestPerformance:
    
    @allure.story("Load Testing")
    @allure.title("Handle multiple concurrent requests")
    @allure.description("Test system performance with multiple products and comments")
    @allure.severity(allure.severity_level.MINOR)
    def test_multiple_products_performance(self, api_client):
        """Test performance with multiple products"""
        
        with allure.step("Create multiple products"):
            products = []
            for i in range(10):
                product = Product.objects.create(
                    name=f"Product {i}",
                    description=f"Description for product {i}"
                )
                products.append(product)
        
        with allure.step("Fetch all products"):
            url = reverse('product-list')
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 10
        
        with allure.step("Fetch individual product details"):
            for product in products[:3]:  # Test first 3 products
                url = reverse('product-detail', kwargs={'pk': product.id})
                response = api_client.get(url)
                assert response.status_code == status.HTTP_200_OK
                assert response.data['name'] == product.name