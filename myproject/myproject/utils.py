import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q
from django.utils import timezone


def analyze_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    Returns: (sentiment_score, sentiment_label)
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Returns -1 to 1
        
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
            
        return round(polarity, 3), label
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 0.0, 'neutral'


def extract_keywords(texts, max_features=20):
    """
    Extract keywords from a list of texts using TF-IDF
    """
    try:
        if not texts:
            return []
            
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Filter out empty texts
        texts = [text for text in texts if text and text.strip()]
        if not texts:
            return []
            
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [{'keyword': kw, 'score': round(score, 3)} for kw, score in keyword_scores]
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []


def calculate_trend_score(product, days=7):
    """
    Calculate trend score for a product based on recent activity
    """
    from .models import Review, ProductAnalytics
    
    try:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get recent reviews
        recent_reviews = product.reviews.filter(
            created_at__date__gte=start_date,
            is_approved=True
        )
        
        # Get recent analytics if available
        recent_analytics = ProductAnalytics.objects.filter(
            product=product,
            date__gte=start_date
        ).aggregate(
            total_views=Count('views'),
            avg_rating=Avg('average_rating'),
            avg_sentiment=Avg('average_sentiment')
        )
        
        # Calculate components
        review_count_score = min(recent_reviews.count() / 10.0, 1.0)  # Max 1.0 for 10+ reviews
        rating_score = (recent_analytics['avg_rating'] or 0) / 5.0  # Normalize to 0-1
        sentiment_score = ((recent_analytics['avg_sentiment'] or 0) + 1) / 2  # Convert -1,1 to 0,1
        view_score = min((recent_analytics['total_views'] or 0) / 100.0, 1.0)  # Max 1.0 for 100+ views
        
        # Weighted combination
        trend_score = (
            review_count_score * 0.3 +
            rating_score * 0.25 +
            sentiment_score * 0.25 +
            view_score * 0.2
        )
        
        return round(trend_score, 3)
    except Exception as e:
        print(f"Error calculating trend score: {e}")
        return 0.0


def get_category_insights(category, days=30):
    """
    Get insights for a category over a period
    """
    from .models import Product, Review
    
    try:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        products = Product.objects.filter(canonical__category=category)
        reviews = Review.objects.filter(
            product__in=products,
            created_at__date__gte=start_date,
            is_approved=True
        )
        
        insights = {
            'total_products': products.count(),
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
            'average_sentiment': reviews.aggregate(avg=Avg('sentiment_score'))['avg'] or 0,
            'sentiment_distribution': {
                'positive': reviews.filter(sentiment_label='positive').count(),
                'negative': reviews.filter(sentiment_label='negative').count(),
                'neutral': reviews.filter(sentiment_label='neutral').count(),
            },
            'top_rated_products': list(
                products.annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ).filter(review_count__gte=3)
                .order_by('-avg_rating')[:5]
                .values('id', 'name', 'avg_rating', 'review_count')
            ),
            'keywords': extract_keywords(list(reviews.values_list('content', flat=True)))[:10]
        }
        
        return insights
    except Exception as e:
        print(f"Error getting category insights: {e}")
        return {}


def get_user_analytics(user):
    """
    Get analytics for a specific user
    """
    from .models import Review
    
    try:
        user_reviews = user.reviews.filter(is_approved=True)
        
        analytics = {
            'total_reviews': user_reviews.count(),
            'average_rating_given': user_reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
            'total_helpful_votes': sum(review.helpful_votes for review in user_reviews),
            'sentiment_distribution': {
                'positive': user_reviews.filter(sentiment_label='positive').count(),
                'negative': user_reviews.filter(sentiment_label='negative').count(),
                'neutral': user_reviews.filter(sentiment_label='neutral').count(),
            },
            'review_frequency': calculate_review_frequency(user_reviews),
            'top_categories': get_user_top_categories(user_reviews),
            'review_timeline': get_user_review_timeline(user_reviews)
        }
        
        return analytics
    except Exception as e:
        print(f"Error getting user analytics: {e}")
        return {}


def calculate_review_frequency(reviews):
    """
    Calculate how frequently a user writes reviews
    """
    if reviews.count() < 2:
        return 0
    
    dates = list(reviews.values_list('created_at__date', flat=True))
    dates.sort()
    
    intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    return round(sum(intervals) / len(intervals), 1) if intervals else 0


def get_user_top_categories(reviews):
    """
    Get user's most reviewed categories
    """
    return list(
        reviews.values('product__canonical__category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )


def get_user_review_timeline(reviews):
    """
    Get user's review timeline for charts
    """
    timeline = []
    reviews_by_month = reviews.extra(
        select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    for item in reviews_by_month:
        timeline.append({
            'month': item['month'],
            'count': item['count']
        })
    
    return timeline


def generate_dashboard_data():
    """
    Generate comprehensive dashboard data for analytics
    """
    from .models import Product, Review, Category, User
    
    try:
        # Overall statistics
        total_products = Product.objects.count()
        total_reviews = Review.objects.filter(is_approved=True).count()
        total_users = User.objects.count()
        total_categories = Category.objects.count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_reviews = Review.objects.filter(
            created_at__gte=thirty_days_ago,
            is_approved=True
        )
        
        # Sentiment analysis
        sentiment_stats = recent_reviews.aggregate(
            avg_sentiment=Avg('sentiment_score'),
            positive_count=Count('id', filter=Q(sentiment_label='positive')),
            negative_count=Count('id', filter=Q(sentiment_label='negative')),
            neutral_count=Count('id', filter=Q(sentiment_label='neutral'))
        )
        
        # Top rated products
        top_products = list(
            Product.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews', filter=Q(reviews__is_approved=True))
            ).filter(review_count__gte=3)
            .order_by('-avg_rating')[:10]
            .values('id', 'name', 'avg_rating', 'review_count')
        )
        
        # Category performance
        category_stats = list(
            Category.objects.annotate(
                product_count=Count('canonicalproduct__listings'),
                review_count=Count('canonicalproduct__listings__reviews', 
                                 filter=Q(canonicalproduct__listings__reviews__is_approved=True)),
                avg_rating=Avg('canonicalproduct__listings__reviews__rating')
            ).order_by('-review_count')[:10]
            .values('id', 'name', 'product_count', 'review_count', 'avg_rating')
        )
        
        # Timeline data (last 12 months)
        timeline_data = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end - timedelta(days=month_end.day)
            
            month_reviews = Review.objects.filter(
                created_at__date__gte=month_start.date(),
                created_at__date__lte=month_end.date(),
                is_approved=True
            )
            
            timeline_data.insert(0, {
                'month': month_start.strftime('%Y-%m'),
                'reviews': month_reviews.count(),
                'avg_rating': month_reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
                'avg_sentiment': month_reviews.aggregate(avg=Avg('sentiment_score'))['avg'] or 0
            })
        
        dashboard_data = {
            'overview': {
                'total_products': total_products,
                'total_reviews': total_reviews,
                'total_users': total_users,
                'total_categories': total_categories,
                'recent_reviews': recent_reviews.count()
            },
            'sentiment': {
                'average': round(sentiment_stats['avg_sentiment'] or 0, 3),
                'distribution': {
                    'positive': sentiment_stats['positive_count'],
                    'negative': sentiment_stats['negative_count'],
                    'neutral': sentiment_stats['neutral_count']
                }
            },
            'top_products': top_products,
            'category_stats': category_stats,
            'timeline': timeline_data,
            'keywords': extract_keywords(
                list(recent_reviews.values_list('content', flat=True))
            )[:15]
        }
        
        return dashboard_data
        
    except Exception as e:
        print(f"Error generating dashboard data: {e}")
        return {}
