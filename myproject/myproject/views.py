from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

from .models import (
    Product, Comment, Review, Category, CanonicalProduct,
    UserProfile, ProductAnalytics, CategoryAnalytics, TrendingProduct
)
from .serializers import (
    ProductSerializer, CommentSerializer, CommentCreateSerializer, CommentApprovalSerializer,
    ReviewSerializer, ReviewCreateSerializer, CategorySerializer, CanonicalProductSerializer,
    UserProfileSerializer, ProductAnalyticsSerializer, CategoryAnalyticsSerializer,
    TrendingProductSerializer, DashboardDataSerializer, UserAnalyticsSerializer,
    CategoryInsightsSerializer
)
from .utils import (
    generate_dashboard_data, get_user_analytics, get_category_insights,
    calculate_trend_score, analyze_sentiment
)


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view products

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get all approved comments for a specific product.
        """
        product = self.get_object()
        comments = product.comments.filter(is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['approve', 'reject']:
            return CommentApprovalSerializer
        return CommentSerializer

    def get_queryset(self):
        """
        Filter comments based on user permissions:
        - Admin users see all comments
        - Regular users see only their own comments
        """
        if self.request.user.is_staff:
            return Comment.objects.all()
        return Comment.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a comment (admin only).
        """
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """
        Reject a comment (admin only).
        """
        comment = self.get_object()
        comment.is_approved = False
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """
        Get all pending comments for admin review.
        """
        pending_comments = Comment.objects.filter(is_approved=False)
        serializer = CommentSerializer(pending_comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def approved(self, request):
        """
        Get all approved comments.
        """
        approved_comments = Comment.objects.filter(is_approved=True)
        serializer = CommentSerializer(approved_comments, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories with analytics.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('canonicalproduct__listings'),
            review_count=Count('canonicalproduct__listings__reviews', 
                             filter=Q(canonicalproduct__listings__reviews__is_approved=True)),
            avg_rating=Avg('canonicalproduct__listings__reviews__rating')
        )

    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """
        Get detailed insights for a category.
        """
        category = self.get_object()
        days = int(request.query_params.get('days', 30))
        insights = get_category_insights(category, days)
        serializer = CategoryInsightsSerializer(insights)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews with analytics.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        """
        Filter reviews based on user permissions.
        """
        queryset = Review.objects.select_related('user', 'product')
        
        if self.request.user.is_staff:
            return queryset.all()
        else:
            return queryset.filter(Q(is_approved=True) | Q(user=self.request.user))

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a review (admin only).
        """
        review = self.get_object()
        review.is_approved = True
        review.save()
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def helpful(self, request, pk=None):
        """
        Mark a review as helpful.
        """
        review = self.get_object()
        review.helpful_votes += 1
        review.save()
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """
        Get all pending reviews for admin review.
        """
        pending_reviews = Review.objects.filter(is_approved=False)
        serializer = ReviewSerializer(pending_reviews, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user profiles with analytics.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Get analytics for a specific user.
        """
        profile = self.get_object()
        analytics = get_user_analytics(profile.user)
        serializer = UserAnalyticsSerializer(analytics)
        return Response(serializer.data)


class TrendingProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing trending products.
    """
    queryset = TrendingProduct.objects.all()
    serializer_class = TrendingProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        period = self.request.query_params.get('period', 'daily')
        days = int(self.request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        return TrendingProduct.objects.filter(
            period=period,
            date__gte=start_date
        ).select_related('product', 'product__canonical', 'product__canonical__category')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dashboard_data(request):
    """
    Get comprehensive dashboard data for analytics.
    """
    data = generate_dashboard_data()
    serializer = DashboardDataSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """
    Get user-specific dashboard data.
    """
    user_analytics = get_user_analytics(request.user)
    serializer = UserAnalyticsSerializer(user_analytics)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_text_sentiment(request):
    """
    Analyze sentiment of provided text.
    """
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    sentiment_score, sentiment_label = analyze_sentiment(text)
    return Response({
        'text': text,
        'sentiment_score': sentiment_score,
        'sentiment_label': sentiment_label
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_analytics(request, product_id):
    """
    Get analytics for a specific product.
    """
    try:
        product = Product.objects.get(id=product_id)
        days = int(request.query_params.get('days', 30))
        
        # Get recent analytics
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = ProductAnalytics.objects.filter(
            product=product,
            date__gte=start_date
        ).order_by('-date')
        
        # Calculate trend score
        trend_score = calculate_trend_score(product, days)
        
        # Get reviews summary
        recent_reviews = product.reviews.filter(
            created_at__date__gte=start_date,
            is_approved=True
        )
        
        data = {
            'product': ProductSerializer(product).data,
            'trend_score': trend_score,
            'analytics': ProductAnalyticsSerializer(analytics, many=True).data,
            'recent_reviews_count': recent_reviews.count(),
            'average_rating': recent_reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
            'sentiment_distribution': {
                'positive': recent_reviews.filter(sentiment_label='positive').count(),
                'negative': recent_reviews.filter(sentiment_label='negative').count(),
                'neutral': recent_reviews.filter(sentiment_label='neutral').count(),
            }
        }
        
        return Response(data)
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
