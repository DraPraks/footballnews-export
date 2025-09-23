#!/usr/bin/env python3
"""
Django script to create dummy users and product data for testing.
This script creates two users with three products each.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_news.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Product

def create_dummy_data():
    """Create two users with three products each."""
    
    print("Creating dummy users and products...")
    
    # Clear existing dummy data (optional)
    User.objects.filter(username__in=['footballer1', 'footballer2']).delete()
    
    # Create user 1
    user1 = User.objects.create_user(
        username='footballer1',
        email='footballer1@example.com',
        password='footballpass123'
    )
    print(f"Created user: {user1.username}")
    
    # Create 3 products for user 1
    products_user1 = [
        {
            'name': 'Manchester United Home Jersey 2024',
            'price': 850000,
            'description': 'Official Manchester United home jersey for the 2024 season. Made with premium materials and authentic team design.',
            'thumbnail': 'https://example.com/images/man-utd-jersey.jpg',
            'category': 'jersey',
            'is_featured': True,
        },
        {
            'name': 'Nike Mercurial Vapor 15',
            'price': 2500000,
            'description': 'Professional football boots designed for speed and agility. Perfect for attacking players who need explosive acceleration.',
            'thumbnail': 'https://example.com/images/nike-mercurial.jpg',
            'category': 'boots',
            'is_featured': False,
        },
        {
            'name': 'UEFA Champions League Official Ball',
            'price': 450000,
            'description': 'Official match ball used in UEFA Champions League. FIFA Quality Pro certified for professional matches.',
            'thumbnail': 'https://example.com/images/ucl-ball.jpg',
            'category': 'ball',
            'is_featured': True,
        }
    ]
    
    for product_data in products_user1:
        product = Product.objects.create(user=user1, **product_data)
        print(f"Created product for {user1.username}: {product.name}")
    
    # Create user 2
    user2 = User.objects.create_user(
        username='footballer2',
        email='footballer2@example.com',
        password='footballpass123'
    )
    print(f"Created user: {user2.username}")
    
    # Create 3 products for user 2
    products_user2 = [
        {
            'name': 'Barcelona Away Jersey 2024',
            'price': 890000,
            'description': 'FC Barcelona away jersey featuring the iconic blaugrana colors. Official licensed product with player-grade quality.',
            'thumbnail': 'https://example.com/images/barca-jersey.jpg',
            'category': 'jersey',
            'is_featured': False,
        },
        {
            'name': 'Adidas Predator Edge',
            'price': 2800000,
            'description': 'Elite football boots with predator technology for enhanced ball control and shooting power. Used by professional players worldwide.',
            'thumbnail': 'https://example.com/images/adidas-predator.jpg',
            'category': 'boots',
            'is_featured': True,
        },
        {
            'name': 'Training Cone Set (20 pieces)',
            'price': 180000,
            'description': 'Professional training cone set for football drills and practice. Durable and lightweight for all weather conditions.',
            'thumbnail': 'https://example.com/images/training-cones.jpg',
            'category': 'training',
            'is_featured': False,
        }
    ]
    
    for product_data in products_user2:
        product = Product.objects.create(user=user2, **product_data)
        print(f"Created product for {user2.username}: {product.name}")
    
    print(f"Created {User.objects.count()} total users")
    print(f"Created {Product.objects.count()} total products")
    print("\nLogin credentials:")
    print("User 1: footballer1 / footballpass123")
    print("User 2: footballer2 / footballpass123")

if __name__ == '__main__':
    create_dummy_data()
