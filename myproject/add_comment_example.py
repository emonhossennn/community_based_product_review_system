#!/usr/bin/env python
"""
Example script showing how to add comments through the API
"""

import requests
import json

def get_auth_token(username, password):
    """Get authentication token for a user"""
    url = "http://localhost:8000/api-token-auth/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json()['token']
        print(f"✓ Got token for user: {username}")
        return token
    else:
        print(f"✗ Failed to get token: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def add_comment(token, product_id, content):
    """Add a comment using the API"""
    url = "http://localhost:8000/api/comments/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    data = {
        "product": product_id,
        "content": content
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        comment = response.json()
        print(f"✓ Comment added successfully!")
        print(f"  Comment ID: {comment['id']}")
        print(f"  Content: {comment['content']}")
        print(f"  Approved: {comment['is_approved']}")
        return comment
    else:
        print(f"✗ Failed to add comment: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_product_comments(product_id):
    """Get all approved comments for a product"""
    url = f"http://localhost:8000/api/products/{product_id}/comments/"
    
    response = requests.get(url)
    if response.status_code == 200:
        comments = response.json()
        print(f"✓ Found {len(comments)} approved comments for product {product_id}")
        for comment in comments:
            print(f"  - {comment['username']}: {comment['content']} ({comment['time_ago']})")
        return comments
    else:
        print(f"✗ Failed to get comments: {response.status_code}")
        return []

def main():
    print("=== Adding Comments via API Example ===")
    
    # Step 1: Get authentication token
    print("\n1. Getting authentication token...")
    token = get_auth_token("testuser", "testpass123")
    if not token:
        print("Make sure the server is running and the user exists!")
        return
    
    # Step 2: Add a comment
    print("\n2. Adding a comment...")
    comment = add_comment(token, 1, "This iPhone 16 is amazing! Great camera and performance.")
    if not comment:
        return
    
    # Step 3: Add another comment
    print("\n3. Adding another comment...")
    comment2 = add_comment(token, 1, "The battery life is incredible. Lasts all day!")
    if not comment2:
        return
    
    # Step 4: Check approved comments (should be empty since comments need admin approval)
    print("\n4. Checking approved comments for product 1...")
    approved_comments = get_product_comments(1)
    
    print("\n" + "=" * 50)
    print("API Comment Addition Complete!")
    print("\nNext steps:")
    print("1. Go to http://localhost:8000/admin/ to approve the comments")
    print("2. After approval, the comments will appear in the product's comment list")
    print("3. Use the API to add more comments as needed")

if __name__ == "__main__":
    main() 