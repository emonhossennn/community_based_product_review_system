from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timesince import timesince
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'


class CanonicalProduct(models.Model):
    canonical_name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    price_range = models.CharField(max_length=50, blank=True)  # e.g., "$10-50"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.canonical_name

    def get_average_rating(self):
        """Calculate average rating across all product listings"""
        from django.db.models import Avg
        avg_rating = 0
        total_ratings = 0
        for product in self.listings.all():
            product_avg = product.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            if product_avg:
                avg_rating += product_avg
                total_ratings += 1
        return avg_rating / total_ratings if total_ratings > 0 else 0

    def get_total_reviews(self):
        """Get total number of reviews across all product listings"""
        total = 0
        for product in self.listings.all():
            total += product.reviews.count()
        return total

    class Meta:
        ordering = ['canonical_name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    canonical = models.ForeignKey(CanonicalProduct, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True)
    seller = models.CharField(max_length=200, blank=True)
    availability = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_average_rating(self):
        """Calculate average rating for this product"""
        avg_rating = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg_rating, 2) if avg_rating else 0

    def get_review_count(self):
        """Get total number of reviews for this product"""
        return self.reviews.count()

    def get_sentiment_score(self):
        """Calculate average sentiment score"""
        reviews = self.reviews.filter(sentiment_score__isnull=False)
        if reviews.exists():
            avg_sentiment = reviews.aggregate(avg_sentiment=Avg('sentiment_score'))['avg_sentiment']
            return round(avg_sentiment, 3) if avg_sentiment else 0
        return 0

    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 stars
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    sentiment_score = models.FloatField(null=True, blank=True)  # -1 to 1
    sentiment_label = models.CharField(max_length=20, blank=True)  # positive, negative, neutral
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.rating} stars by {self.user.username}"

    def get_time_ago(self):
        """Returns relative time like '10 days ago'"""
        return timesince(self.created_at, timezone.now())

    def save(self, *args, **kwargs):
        # Auto-calculate sentiment on save
        if self.content and not self.sentiment_score:
            from .utils import analyze_sentiment
            self.sentiment_score, self.sentiment_label = analyze_sentiment(self.content)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"

    def get_time_ago(self):
        """Returns relative time like '10 days ago'"""
        return timesince(self.created_at, timezone.now())

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True)
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating_given = models.FloatField(default=0.0)
    helpful_votes_received = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_stats(self):
        """Update user statistics"""
        reviews = self.user.reviews.all()
        self.total_reviews = reviews.count()
        if self.total_reviews > 0:
            avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            self.average_rating_given = round(avg_rating, 2) if avg_rating else 0
        
        self.helpful_votes_received = sum(review.helpful_votes for review in reviews)
        self.save()


class ProductAnalytics(models.Model):
    """Daily analytics snapshot for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    average_sentiment = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)  # reviews / views
    
    def __str__(self):
        return f"{self.product.name} - {self.date}"

    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date']


class CategoryAnalytics(models.Model):
    """Daily analytics snapshot for categories"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    total_products = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    average_sentiment = models.FloatField(default=0.0)
    top_products = models.JSONField(default=list)  # List of top product IDs
    
    def __str__(self):
        return f"{self.category.name} - {self.date}"

    class Meta:
        unique_together = ['category', 'date']
        ordering = ['-date']


class TrendingProduct(models.Model):
    """Track trending products based on various metrics"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    trend_score = models.FloatField()  # Composite score based on views, reviews, sentiment
    rank = models.PositiveIntegerField()
    period = models.CharField(max_length=20)  # 'daily', 'weekly', 'monthly'
    date = models.DateField()
    
    def __str__(self):
        return f"{self.product.name} - Rank {self.rank} ({self.period})"

    class Meta:
        unique_together = ['product', 'period', 'date']
        ordering = ['rank', '-date']
