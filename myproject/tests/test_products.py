"""
Product API Tests with Allure reporting
"""
import pytest
import allure
from rest_framework import status
from rest_framework.test import APITestCase
from myproject.models import Product

@allure.epic("Product Review System")
@allure.feature("Product Management")
class TestProductAPI(APITestCase):
    
    @allure.story("Product Listing")
    @allure.title("Get all products - Public access")
    @allure.description("Test that anyone can view the list of products without authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_products_public_access(self):
        """Test getting all products without authentication"""
        with allure.step("Create sample products"):
            Product.objects.create(name="iPhone 16", description="Latest iPhone")
            Product.objects.create(name="Samsung Galaxy", description="Android phone")
        
        with allure.step("Make GET request to products endpoint"):
            url = '/api/products/'
            response = self.client.get(url)
        
        with allure.step("Verify response"):
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 2
            
        allure.attach(
            str(response.data),
            name="Response Data",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("Product Details")
    @allure.title("Get specific product details")
    @allure.description("Test retrieving details of a specific product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_detail(self):
        """Test getting specific product details"""
        with allure.step("Create a product"):
            product = Product.objects.create(
                name="MacBook Pro", 
                description="Professional laptop"
            )
        
        with allure.step("Request product details"):
            url = f'/api/products/{product.id}/'
            response = self.client.get(url)
        
        with allure.step("Verify product details"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data['name'] == "MacBook Pro"
            assert response.data['description'] == "Professional laptop"
    
    @allure.story("Product Comments")
    @allure.title("Get approved comments for product")
    @allure.description("Test retrieving only approved comments for a specific product")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_product_comments(self):
        """Test getting approved comments for a product"""
        with allure.step("Create a product"):
            product = Product.objects.create(name="Test Product")
        
        with allure.step("Request product comments"):
            url = f'/api/products/{product.id}/comments/'
            response = self.client.get(url)
        
        with allure.step("Verify empty comments list"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data == []
    
    @allure.story("Error Handling")
    @allure.title("Handle non-existent product")
    @allure.description("Test proper error handling for non-existent product")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_nonexistent_product(self):
        """Test getting a non-existent product returns 404"""
        with allure.step("Request non-existent product"):
            url = '/api/products/999/'
            response = self.client.get(url)
        
        with allure.step("Verify 404 response"):
            assert response.status_code == status.HTTP_404_NOT_FOUND