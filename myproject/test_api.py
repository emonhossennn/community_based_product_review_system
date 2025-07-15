#!/usr/bin/env python
"""
Test script for the Community-Based Product Review System API
Run this script to test the API functionality
"""

import os
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import Product, Comment

def create_sample_data():
    """Create sample products and users for testing"""
    print("Creating sample data...")
    
    # Create a regular user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'testuser@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    
    # Create sample products
    products_data = [
        {'name': 'iPhone 16', 'description': 'Latest iPhone model with advanced features'},
        {'name': 'Samsung Galaxy S25', 'description': 'Premium Android smartphone'},
        {'name': 'MacBook Pro M3', 'description': 'Professional laptop for developers'},
    ]
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={'description': data['description']}
        )
        if created:
            print(f"Created product: {product.name}")
        products.append(product)
    
    return user, products

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:8000/api"
    
    print("\n=== Testing API Endpoints ===")
    
    # Test 1: Get all products (public access)
    print("\n1. Getting all products...")
    try:
        response = requests.get(f"{base_url}/products/")
        if response.status_code == 200:
            products_data = response.json()
            print(f"✓ Found {len(products_data)} products")
            for product in products_data:
                description = product.get('description', 'No description')
                print(f"  - {product['name']}: {description[:50]}...")
        else:
            print(f"✗ Failed to get products: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Server not running. Please start the server with: python manage.py runserver")
        return
    
    # Test 2: Get comments for a product (should be empty initially)
    if products_data:
        product_id = products_data[0]['id']
        print(f"\n2. Getting comments for product {product_id}...")
        response = requests.get(f"{base_url}/products/{product_id}/comments/")
        if response.status_code == 200:
            comments = response.json()
            print(f"✓ Found {len(comments)} approved comments")
        else:
            print(f"✗ Failed to get comments: {response.status_code}")

def main():
    print("Community-Based Product Review System - API Test")
    print("=" * 50)
    
    # Create sample data
    user, products = create_sample_data()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("API Test Complete!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/admin/ to manage products and comments")
    print("2. Use the API endpoints to create and manage comments")
    print("3. Check the README.md file for detailed API documentation")
    print("\nSample API calls:")
    print("- GET /api/products/ (view all products)")
    print("- GET /api/products/1/comments/ (view approved comments for product 1)")
    print("- POST /api/comments/ (create a comment - requires authentication)")

if __name__ == "__main__":
    main() 