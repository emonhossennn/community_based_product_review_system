import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from myproject.models import (
    Category, CanonicalProduct, Product, Review, Comment, UserProfile,
    ProductAnalytics, CategoryAnalytics, TrendingProduct
)

fake = Faker()


class Command(BaseCommand):
    help = 'Generate sample data for analytics demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='Number of categories to create'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=500,
            help='Number of reviews to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting sample data generation...')
        
        # Create users
        self.stdout.write('Creating users...')
        users = self.create_users(options['users'])
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories = self.create_categories(options['categories'])
        
        # Create products
        self.stdout.write('Creating products...')
        products = self.create_products(categories, options['products'])
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        reviews = self.create_reviews(users, products, options['reviews'])
        
        # Create analytics data
        self.stdout.write('Creating analytics data...')
        self.create_analytics_data(products, categories)
        
        # Create trending products
        self.stdout.write('Creating trending products...')
        self.create_trending_products(products)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(users)} users\n'
                f'- {len(categories)} categories\n'
                f'- {len(products)} products\n'
                f'- {len(reviews)} reviews'
            )
        )

    def create_users(self, count):
        users = []
        
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
        # Create admin profile
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'bio': 'Administrator of the product review system',
                'location': 'New York, NY'
            }
        )
        
        users.append(admin_user)
        
        # Create regular users
        for i in range(count - 1):
            username = fake.user_name() + str(random.randint(1, 999))
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=200),
                location=fake.city() + ', ' + fake.state_abbr(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80)
            )
            
            users.append(user)
        
        return users

    def create_categories(self, count):
        category_names = [
            'Electronics', 'Books', 'Clothing', 'Home & Kitchen', 'Sports & Outdoors',
            'Health & Beauty', 'Toys & Games', 'Automotive', 'Garden & Tools', 'Music',
            'Movies & TV', 'Software', 'Office Products', 'Pet Supplies', 'Grocery'
        ]
        
        categories = []
        for i in range(min(count, len(category_names))):
            category = Category.objects.create(
                name=category_names[i],
                description=fake.text(max_nb_chars=150)
            )
            categories.append(category)
        
        return categories

    def create_products(self, categories, count):
        products = []
        brands = ['Apple', 'Samsung', 'Sony', 'Nike', 'Adidas', 'Amazon', 'Microsoft', 'Google', 'Dell', 'HP']
        
        for i in range(count):
            category = random.choice(categories)
            
            # Create canonical product
            canonical_product = CanonicalProduct.objects.create(
                canonical_name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=300),
                category=category,
                brand=random.choice(brands),
                price_range=f"${random.randint(10, 100)}-{random.randint(100, 1000)}"
            )
            
            # Create 1-3 product listings for each canonical product
            listings_count = random.randint(1, 3)
            for j in range(listings_count):
                product = Product.objects.create(
                    name=canonical_product.canonical_name + (f" - Variant {j+1}" if listings_count > 1 else ""),
                    description=fake.text(max_nb_chars=400),
                    canonical=canonical_product,
                    price=random.uniform(10, 1000),
                    image_url=fake.image_url(),
                    seller=fake.company(),
                    availability=random.choice([True, True, True, False]),  # 75% available
                    view_count=random.randint(0, 1000)
                )
                products.append(product)
        
        return products

    def create_reviews(self, users, products, count):
        reviews = []
        review_titles = [
            "Great product!", "Not what I expected", "Amazing quality", "Poor quality",
            "Love it!", "Terrible experience", "Good value for money", "Overpriced",
            "Highly recommend", "Would not buy again", "Perfect!", "Okay product",
            "Exceeded expectations", "Below average", "Fantastic purchase"
        ]
        
        positive_reviews = [
            "This product is amazing! I love everything about it. The quality is top-notch and it exceeded my expectations.",
            "Fantastic purchase! Really happy with this item. Great value for money and excellent customer service.",
            "Outstanding quality! This product works perfectly and looks great. Highly recommend to everyone.",
            "Perfect! Exactly what I was looking for. The design is beautiful and functionality is excellent.",
            "Excellent product! Very satisfied with my purchase. Fast shipping and great packaging too.",
        ]
        
        negative_reviews = [
            "Very disappointed with this product. The quality is poor and it doesn't work as advertised.",
            "Waste of money! This product broke after just a few days. Poor build quality and terrible customer service.",
            "Not recommended. The product has many issues and doesn't live up to the hype. Very frustrating experience.",
            "Poor quality materials and bad design. This product is overpriced for what you get. Very unsatisfied.",
            "Terrible experience! The product arrived damaged and customer service was unhelpful. Would not buy again.",
        ]
        
        neutral_reviews = [
            "It's an okay product. Nothing special but does the job. Could be better for the price.",
            "Average quality. The product works but has some minor issues. Not bad but not great either.",
            "Decent product overall. Some good features but also some drawbacks. It's acceptable.",
            "The product is fine. It works as expected but doesn't exceed expectations. Fair value.",
            "Not bad, not great. The product has its pros and cons. It's a reasonable purchase.",
        ]
        
        for i in range(count):
            user = random.choice(users)
            product = random.choice(products)
            
            # Skip if user already reviewed this product
            if Review.objects.filter(user=user, product=product).exists():
                continue
            
            rating = random.randint(1, 5)
            
            # Choose review content based on rating
            if rating >= 4:
                content = random.choice(positive_reviews)
            elif rating <= 2:
                content = random.choice(negative_reviews)
            else:
                content = random.choice(neutral_reviews)
            
            # Create review with random date in the last 6 months
            created_date = fake.date_time_between(
                start_date='-6m', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            )
            
            review = Review.objects.create(
                product=product,
                user=user,
                title=random.choice(review_titles),
                content=content,
                rating=rating,
                is_verified_purchase=random.choice([True, False]),
                helpful_votes=random.randint(0, 50),
                is_approved=random.choice([True, True, True, False]),  # 75% approved
                created_at=created_date,
                updated_at=created_date
            )
            
            reviews.append(review)
        
        return reviews

    def create_analytics_data(self, products, categories):
        # Generate daily analytics for the last 30 days
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            
            # Product analytics
            for product in random.sample(products, min(len(products), 50)):  # Random 50 products
                ProductAnalytics.objects.get_or_create(
                    product=product,
                    date=date,
                    defaults={
                        'views': random.randint(10, 500),
                        'reviews_count': random.randint(0, 20),
                        'average_rating': round(random.uniform(1, 5), 2),
                        'average_sentiment': round(random.uniform(-1, 1), 3),
                        'conversion_rate': round(random.uniform(0, 0.3), 3)
                    }
                )
            
            # Category analytics
            for category in categories:
                CategoryAnalytics.objects.get_or_create(
                    category=category,
                    date=date,
                    defaults={
                        'total_products': random.randint(5, 30),
                        'total_reviews': random.randint(20, 200),
                        'average_rating': round(random.uniform(2, 5), 2),
                        'average_sentiment': round(random.uniform(-0.5, 0.8), 3),
                        'top_products': [
                            random.choice(products).id for _ in range(5)
                        ]
                    }
                )

    def create_trending_products(self, products):
        periods = ['daily', 'weekly', 'monthly']
        
        for period in periods:
            # Generate trending products for the last 7 days
            for i in range(7):
                date = timezone.now().date() - timedelta(days=i)
                
                # Select random products and assign rankings
                trending_products = random.sample(products, min(len(products), 20))
                
                for rank, product in enumerate(trending_products, 1):
                    TrendingProduct.objects.get_or_create(
                        product=product,
                        period=period,
                        date=date,
                        defaults={
                            'trend_score': round(random.uniform(0, 1), 3),
                            'rank': rank
                        }
                    )
