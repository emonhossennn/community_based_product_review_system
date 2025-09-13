from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Product, Comment, Review, Category, CanonicalProduct,
    UserProfile, ProductAnalytics, CategoryAnalytics, TrendingProduct
)


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'product_count', 'review_count', 'avg_rating']


class CanonicalProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(source='get_average_rating', read_only=True)
    total_reviews = serializers.IntegerField(source='get_total_reviews', read_only=True)
    
    class Meta:
        model = CanonicalProduct
        fields = ['id', 'canonical_name', 'description', 'category', 'brand', 'price_range', 
                 'created_at', 'average_rating', 'total_reviews']


class ProductSerializer(serializers.ModelSerializer):
    canonical = CanonicalProductSerializer(read_only=True)
    average_rating = serializers.FloatField(source='get_average_rating', read_only=True)
    review_count = serializers.IntegerField(source='get_review_count', read_only=True)
    sentiment_score = serializers.FloatField(source='get_sentiment_score', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'canonical', 'price', 'image_url', 'seller',
                 'availability', 'view_count', 'created_at', 'updated_at', 'average_rating',
                 'review_count', 'sentiment_score']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    time_ago = serializers.CharField(source='get_time_ago', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'username', 'title', 'content', 
                 'rating', 'is_verified_purchase', 'helpful_votes', 'sentiment_score', 
                 'sentiment_label', 'is_approved', 'created_at', 'updated_at', 'time_ago']
        read_only_fields = ['user', 'sentiment_score', 'sentiment_label', 'is_approved', 
                          'created_at', 'updated_at', 'time_ago']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'title', 'content', 'rating', 'is_verified_purchase']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'date_joined', 'bio', 'location', 'birth_date', 
                 'avatar', 'total_reviews', 'average_rating_given', 'helpful_votes_received', 
                 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    time_ago = serializers.CharField(source='get_time_ago', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'product', 'user', 'username', 'content', 'is_approved', 'created_at', 'time_ago']
        read_only_fields = ['user', 'is_approved', 'created_at', 'time_ago']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['product', 'content']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['is_approved']


class ProductAnalyticsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductAnalytics
        fields = ['id', 'product', 'product_name', 'date', 'views', 'reviews_count', 
                 'average_rating', 'average_sentiment', 'conversion_rate']


class CategoryAnalyticsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CategoryAnalytics
        fields = ['id', 'category', 'category_name', 'date', 'total_products', 'total_reviews',
                 'average_rating', 'average_sentiment', 'top_products']


class TrendingProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.canonical.category.name', read_only=True)
    
    class Meta:
        model = TrendingProduct
        fields = ['id', 'product', 'product_name', 'category_name', 'trend_score', 
                 'rank', 'period', 'date']


class DashboardDataSerializer(serializers.Serializer):
    overview = serializers.DictField()
    sentiment = serializers.DictField()
    top_products = serializers.ListField()
    category_stats = serializers.ListField()
    timeline = serializers.ListField()
    keywords = serializers.ListField()


class UserAnalyticsSerializer(serializers.Serializer):
    total_reviews = serializers.IntegerField()
    average_rating_given = serializers.FloatField()
    total_helpful_votes = serializers.IntegerField()
    sentiment_distribution = serializers.DictField()
    review_frequency = serializers.FloatField()
    top_categories = serializers.ListField()
    review_timeline = serializers.ListField()


class CategoryInsightsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    average_sentiment = serializers.FloatField()
    sentiment_distribution = serializers.DictField()
    top_rated_products = serializers.ListField()
    keywords = serializers.ListField()
