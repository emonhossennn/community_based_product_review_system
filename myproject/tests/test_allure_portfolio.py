"""
Advanced SQA Portfolio Test Suite with Allure Reporting
Demonstrates professional testing skills for resume showcase
"""
import pytest
import allure
import json
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from myproject.models import Product, Comment
from datetime import datetime, timedelta
import time

@allure.epic("SQA Portfolio Showcase")
@allure.feature("Advanced API Testing")
@allure.tag("portfolio", "api", "authentication")
class TestAdvancedAPIPortfolio(APITestCase):
    """
    Advanced test suite demonstrating professional SQA skills:
    - Comprehensive API testing
    - Security testing
    - Performance validation
    - Data integrity testing
    - Error handling validation
    """
    
    def setUp(self):
        """Setup test environment with realistic data"""
        # Create test users with different roles
        self.regular_user = User.objects.create_user(
            username='john_doe',
            email='john.doe@company.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin_sarah',
            email='sarah.admin@company.com',
            password='AdminPass456!',
            first_name='Sarah',
            last_name='Admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.moderator_user = User.objects.create_user(
            username='mod_mike',
            email='mike.mod@company.com',
            password='ModPass789!',
            is_staff=True
        )
        
        # Create realistic product catalog
        self.products = [
            Product.objects.create(
                name="iPhone 16 Pro Max",
                description="Latest flagship smartphone with advanced AI capabilities and professional camera system"
            ),
            Product.objects.create(
                name="MacBook Pro M3 16-inch",
                description="Professional laptop with M3 Max chip, perfect for developers and content creators"
            ),
            Product.objects.create(
                name="Samsung Galaxy S25 Ultra",
                description="Premium Android smartphone with S Pen and exceptional display quality"
            )
        ]
        
        # Create tokens for authentication
        self.user_token, _ = Token.objects.get_or_create(user=self.regular_user)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.mod_token, _ = Token.objects.get_or_create(user=self.moderator_user)

    @allure.story("Security Testing")
    @allure.title("Comprehensive Authentication Security Validation")
    @allure.description("Validates authentication mechanisms and security controls")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.testcase("TC-SEC-001")
    def test_comprehensive_authentication_security(self):
        """Test comprehensive authentication security scenarios"""
        
        with allure.step("Test 1: Verify unauthenticated access is properly blocked"):
            comment_data = {
                'product': self.products[0].id,
                'content': 'Unauthorized comment attempt'
            }
            response = self.client.post('/api/comments/', comment_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            allure.attach(
                json.dumps(response.data, indent=2),
                name="Unauthorized Response",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Test 2: Verify invalid token is rejected"):
            self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_12345')
            response = self.client.post('/api/comments/', comment_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        with allure.step("Test 3: Verify malformed authorization header"):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_format')
            response = self.client.post('/api/comments/', comment_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        with allure.step("Test 4: Verify valid token works correctly"):
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            response = self.client.post('/api/comments/', comment_data)
            assert response.status_code == status.HTTP_201_CREATED
            
            allure.attach(
                json.dumps(response.data, indent=2),
                name="Successful Authentication Response",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("Authorization Testing")
    @allure.title("Role-Based Access Control Validation")
    @allure.description("Comprehensive testing of user permissions and role-based access")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("TC-AUTH-002")
    def test_role_based_access_control(self):
        """Test role-based access control across different user types"""
        
        # Create a test comment for permission testing
        test_comment = Comment.objects.create(
            product=self.products[0],
            user=self.regular_user,
            content="Test comment for permission validation",
            is_approved=False
        )
        
        with allure.step("Test 1: Regular user cannot access admin endpoints"):
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            # Try to approve comment (admin only)
            response = self.client.patch(f'/api/comments/{test_comment.id}/approve/')
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            # Try to access pending comments (admin only)
            response = self.client.get('/api/comments/pending/')
            assert response.status_code == status.HTTP_403_FORBIDDEN
        
        with allure.step("Test 2: Admin user can access all endpoints"):
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
            
            # Approve comment
            response = self.client.patch(f'/api/comments/{test_comment.id}/approve/')
            assert response.status_code == status.HTTP_200_OK
            
            # Access pending comments
            response = self.client.get('/api/comments/pending/')
            assert response.status_code == status.HTTP_200_OK
            
            # Access all comments
            response = self.client.get('/api/comments/')
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) >= 1
        
        with allure.step("Test 3: User can only see their own comments"):
            # Create another user and comment
            other_user = User.objects.create_user('other_user', 'other@test.com', 'pass')
            other_token, _ = Token.objects.get_or_create(user=other_user)
            
            Comment.objects.create(
                product=self.products[1],
                user=other_user,
                content="Other user's comment"
            )
            
            # Regular user should only see their own comments
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            response = self.client.get('/api/comments/')
            assert response.status_code == status.HTTP_200_OK
            
            # Verify user only sees their own comments
            user_comments = [c for c in response.data if c['user'] == self.regular_user.id]
            other_comments = [c for c in response.data if c['user'] == other_user.id]
            assert len(user_comments) >= 1
            assert len(other_comments) == 0

    @allure.story("Data Validation Testing")
    @allure.title("Comprehensive Input Validation and Data Integrity")
    @allure.description("Tests data validation, boundary conditions, and data integrity")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("TC-VAL-003")
    def test_comprehensive_data_validation(self):
        """Test comprehensive data validation scenarios"""
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        
        with allure.step("Test 1: Empty content validation"):
            invalid_data = {'product': self.products[0].id, 'content': ''}
            response = self.client.post('/api/comments/', invalid_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test 2: Whitespace-only content validation"):
            invalid_data = {'product': self.products[0].id, 'content': '   \n\t   '}
            response = self.client.post('/api/comments/', invalid_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test 3: Missing required fields"):
            # Missing product
            response = self.client.post('/api/comments/', {'content': 'Comment without product'})
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            
            # Missing content
            response = self.client.post('/api/comments/', {'product': self.products[0].id})
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test 4: Invalid product ID"):
            invalid_data = {'product': 99999, 'content': 'Comment for non-existent product'}
            response = self.client.post('/api/comments/', invalid_data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test 5: SQL injection attempt"):
            malicious_content = "'; DROP TABLE myproject_comment; --"
            comment_data = {'product': self.products[0].id, 'content': malicious_content}
            response = self.client.post('/api/comments/', comment_data)
            
            # Should create comment safely (Django ORM protects against SQL injection)
            assert response.status_code == status.HTTP_201_CREATED
            
            # Verify the malicious content is stored as plain text
            assert response.data['content'] == malicious_content
            
            # Verify database integrity
            assert Comment.objects.filter(content=malicious_content).exists()
        
        with allure.step("Test 6: XSS attempt validation"):
            xss_content = "<script>alert('XSS')</script>Malicious comment"
            comment_data = {'product': self.products[0].id, 'content': xss_content}
            response = self.client.post('/api/comments/', comment_data)
            
            assert response.status_code == status.HTTP_201_CREATED
            # Content should be stored as-is (frontend should handle escaping)
            assert response.data['content'] == xss_content
        
        with allure.step("Test 7: Very long content validation"):
            long_content = "A" * 10000  # Very long string
            comment_data = {'product': self.products[0].id, 'content': long_content}
            response = self.client.post('/api/comments/', comment_data)
            
            # Should handle long content appropriately
            if response.status_code == status.HTTP_201_CREATED:
                assert len(response.data['content']) == 10000
            else:
                # If there's a length limit, it should return 400
                assert response.status_code == status.HTTP_400_BAD_REQUEST

    @allure.story("Performance Testing")
    @allure.title("API Performance and Load Testing")
    @allure.description("Tests API performance under various load conditions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("TC-PERF-004")
    def test_api_performance_validation(self):
        """Test API performance and response times"""
        
        with allure.step("Test 1: Response time validation for product listing"):
            start_time = time.time()
            response = self.client.get('/api/products/')
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            assert response.status_code == status.HTTP_200_OK
            assert response_time < 1000  # Should respond within 1 second
            
            allure.attach(
                f"Response time: {response_time:.2f}ms",
                name="Product List Response Time",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Test 2: Bulk comment creation performance"):
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            start_time = time.time()
            created_comments = []
            
            # Create multiple comments
            for i in range(5):
                comment_data = {
                    'product': self.products[i % len(self.products)].id,
                    'content': f'Performance test comment #{i+1} with detailed content about the product'
                }
                response = self.client.post('/api/comments/', comment_data)
                assert response.status_code == status.HTTP_201_CREATED
                created_comments.append(response.data['id'])
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            avg_time = total_time / 5
            
            assert avg_time < 500  # Average should be under 500ms per comment
            
            allure.attach(
                f"Total time: {total_time:.2f}ms\nAverage per comment: {avg_time:.2f}ms",
                name="Bulk Comment Creation Performance",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Test 3: Concurrent read operations"):
            # Simulate multiple concurrent reads
            responses = []
            start_time = time.time()
            
            for product in self.products:
                response = self.client.get(f'/api/products/{product.id}/')
                responses.append(response)
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
            
            assert total_time < 2000  # All reads should complete within 2 seconds

    @allure.story("Integration Testing")
    @allure.title("End-to-End Workflow Validation")
    @allure.description("Complete user journey from registration to comment approval")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("TC-E2E-005")
    def test_complete_user_journey(self):
        """Test complete end-to-end user journey"""
        
        with allure.step("Step 1: User browses products (public access)"):
            response = self.client.get('/api/products/')
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) >= 3
            
            # Select a product for commenting
            selected_product = response.data[0]
            product_id = selected_product['id']
            
            allure.attach(
                json.dumps(selected_product, indent=2),
                name="Selected Product",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 2: User views product details and existing comments"):
            # Get product details
            response = self.client.get(f'/api/products/{product_id}/')
            assert response.status_code == status.HTTP_200_OK
            
            # Get existing comments (should only show approved ones)
            response = self.client.get(f'/api/products/{product_id}/comments/')
            assert response.status_code == status.HTTP_200_OK
            initial_comment_count = len(response.data)
        
        with allure.step("Step 3: User creates account and posts comment"):
            # Authenticate user
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            # Create detailed comment
            comment_data = {
                'product': product_id,
                'content': 'Excellent product! The build quality is outstanding and the performance exceeds expectations. Highly recommended for professional use.'
            }
            response = self.client.post('/api/comments/', comment_data)
            assert response.status_code == status.HTTP_201_CREATED
            
            comment_id = response.data['id']
            assert response.data['is_approved'] == False  # Should be pending
            
            allure.attach(
                json.dumps(response.data, indent=2),
                name="Created Comment",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 4: Verify comment is not publicly visible yet"):
            # Clear authentication to test public view
            self.client.credentials()
            response = self.client.get(f'/api/products/{product_id}/comments/')
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == initial_comment_count  # No new comments visible
        
        with allure.step("Step 5: Admin reviews and approves comment"):
            # Authenticate as admin
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
            
            # Check pending comments
            response = self.client.get('/api/comments/pending/')
            assert response.status_code == status.HTTP_200_OK
            pending_comments = [c for c in response.data if c['id'] == comment_id]
            assert len(pending_comments) == 1
            
            # Approve the comment
            response = self.client.patch(f'/api/comments/{comment_id}/approve/')
            assert response.status_code == status.HTTP_200_OK
        
        with allure.step("Step 6: Verify comment is now publicly visible"):
            # Clear authentication for public view
            self.client.credentials()
            response = self.client.get(f'/api/products/{product_id}/comments/')
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == initial_comment_count + 1
            
            # Find our approved comment
            approved_comment = next((c for c in response.data if c['id'] == comment_id), None)
            assert approved_comment is not None
            assert approved_comment['is_approved'] == True
            
            allure.attach(
                json.dumps(approved_comment, indent=2),
                name="Approved Comment (Public View)",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 7: User can update their approved comment"):
            # Re-authenticate as user
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            updated_content = 'Updated: Excellent product! After using it for a week, I can confirm it exceeds all expectations.'
            response = self.client.patch(
                f'/api/comments/{comment_id}/',
                {'content': updated_content}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data['content'] == updated_content

    @allure.story("Error Handling")
    @allure.title("Comprehensive Error Handling Validation")
    @allure.description("Tests system behavior under error conditions and edge cases")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("TC-ERR-006")
    def test_comprehensive_error_handling(self):
        """Test comprehensive error handling scenarios"""
        
        with allure.step("Test 1: 404 errors for non-existent resources"):
            # Non-existent product
            response = self.client.get('/api/products/99999/')
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            # Non-existent comment
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            response = self.client.get('/api/comments/99999/')
            assert response.status_code == status.HTTP_404_NOT_FOUND
        
        with allure.step("Test 2: Method not allowed errors"):
            # Try to DELETE on list endpoint
            response = self.client.delete('/api/products/')
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
            
            # Try to POST on detail endpoint
            response = self.client.post('/api/products/1/')
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        with allure.step("Test 3: Content-Type validation"):
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            # Send invalid JSON
            response = self.client.post(
                '/api/comments/',
                'invalid json content',
                content_type='application/json'
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        with allure.step("Test 4: Rate limiting simulation"):
            # This would test rate limiting if implemented
            # For now, we'll test rapid successive requests
            responses = []
            for i in range(10):
                response = self.client.get('/api/products/')
                responses.append(response.status_code)
            
            # All should succeed (no rate limiting implemented)
            assert all(status_code == 200 for status_code in responses)
        
        with allure.step("Test 5: Malformed request handling"):
            # Test with missing headers, malformed data, etc.
            test_cases = [
                {'data': None, 'expected': 400},
                {'data': {}, 'expected': 400},
                {'data': {'invalid_field': 'value'}, 'expected': 400},
            ]
            
            for case in test_cases:
                response = self.client.post('/api/comments/', case['data'])
                # Should handle gracefully (either 400 or 401 for auth)
                assert response.status_code in [400, 401]

    @allure.story("Data Consistency")
    @allure.title("Database Consistency and Transaction Testing")
    @allure.description("Validates data consistency and transaction integrity")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("TC-DATA-007")
    def test_data_consistency_validation(self):
        """Test data consistency and integrity"""
        
        with allure.step("Test 1: Comment count consistency"):
            initial_count = Comment.objects.count()
            
            # Create multiple comments
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
            
            created_ids = []
            for i in range(3):
                comment_data = {
                    'product': self.products[0].id,
                    'content': f'Consistency test comment {i+1}'
                }
                response = self.client.post('/api/comments/', comment_data)
                assert response.status_code == status.HTTP_201_CREATED
                created_ids.append(response.data['id'])
            
            # Verify count increased correctly
            final_count = Comment.objects.count()
            assert final_count == initial_count + 3
        
        with allure.step("Test 2: User-comment relationship integrity"):
            # Verify all created comments belong to the correct user
            user_comments = Comment.objects.filter(user=self.regular_user)
            assert user_comments.count() >= 3
            
            for comment in user_comments:
                assert comment.user_id == self.regular_user.id
        
        with allure.step("Test 3: Product-comment relationship integrity"):
            # Verify comments are properly linked to products
            product_comments = Comment.objects.filter(product=self.products[0])
            assert product_comments.count() >= 3
            
            for comment in product_comments:
                assert comment.product_id == self.products[0].id
        
        with allure.step("Test 4: Approval status consistency"):
            # Verify new comments default to unapproved
            recent_comments = Comment.objects.filter(user=self.regular_user).order_by('-created_at')[:3]
            
            for comment in recent_comments:
                assert comment.is_approved == False
            
            # Approve one comment and verify status change
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
            comment_to_approve = recent_comments[0]
            
            response = self.client.patch(f'/api/comments/{comment_to_approve.id}/approve/')
            assert response.status_code == status.HTTP_200_OK
            
            # Verify database was updated
            comment_to_approve.refresh_from_db()
            assert comment_to_approve.is_approved == True

    def tearDown(self):
        """Clean up after tests"""
        # Clean up is handled automatically by Django test framework
        # This method is here to demonstrate proper test cleanup practices
        pass