# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Django REST Framework API for a **Community-Based Product Review System** with admin approval workflow. The system manages products, reviews, comments, and includes analytics capabilities with sentiment analysis.

## Essential Development Commands

### Environment Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py makemigrations myproject
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Development Server
```powershell
# Start development server
python manage.py runserver

# Access admin interface
# Navigate to: http://localhost:8000/admin/
# API endpoints: http://localhost:8000/api/
```

### Testing
```powershell
# Run all tests with pytest
pytest

# Run tests with Allure reporting
pytest --allure-dir=allure-results

# Run specific test file
pytest tests/test_api_clean.py

# Run tests for specific functionality
pytest tests/test_products.py
pytest tests/test_comments.py
pytest tests/test_integration.py

# Generate and view Allure report
run_allure.bat
```

### Database Operations
```powershell
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Create test data
python test_api.py
```

## Architecture Overview

### Core Model Hierarchy
The system follows a sophisticated product organization structure:

1. **Category** → **CanonicalProduct** → **Product** (listings) → **Reviews/Comments**
   - `Category`: Product categories (e.g., Electronics, Books)
   - `CanonicalProduct`: Abstract product representation (e.g., "iPhone 16")
   - `Product`: Specific product listings with seller info and pricing
   - `Review`: Detailed reviews with ratings and sentiment analysis
   - `Comment`: Simple comments requiring admin approval

2. **User Management**:
   - `UserProfile`: Extended user information with analytics
   - Token-based authentication for API access
   - Admin vs regular user permission system

### Key Architectural Patterns

**Approval Workflow System**:
- Comments default to `is_approved=False`
- Admin-only endpoints for approval/rejection
- Separate querysets for public vs admin views

**Analytics Integration**:
- Automatic sentiment analysis using TextBlob
- Daily analytics snapshots (`ProductAnalytics`, `CategoryAnalytics`)
- Trending product calculations with composite scoring
- Real-time dashboard data generation

**Permission Architecture**:
- `IsAdminUser` custom permission class
- ViewSet-level permission filtering
- User-specific data isolation (users only see own content)

### API Structure

**ViewSet Organization**:
- `ProductViewSet`: Read-only product viewing with nested comments
- `CommentViewSet`: Full CRUD with admin approval actions
- `ReviewViewSet`: Advanced review management with sentiment analysis
- `CategoryViewSet`: Category insights and analytics
- `UserProfileViewSet`: User analytics and profile management

**Custom Actions Pattern**:
- `@action(detail=True)`: Instance-specific actions (approve, reject)
- `@action(detail=False)`: Collection actions (pending, approved)
- Analytics endpoints separated from CRUD operations

## Development Patterns

### Model Methods
Models include computed properties and business logic:
```python
# Product ratings and analytics
product.get_average_rating()
product.get_sentiment_score()

# User statistics
user_profile.update_stats()

# Time-based utilities
comment.get_time_ago()
```

### Serializer Strategy
- Separate serializers for create vs read operations
- Context-aware serializers that include related data
- Automatic user assignment in `create()` methods

### Testing Architecture
- Pytest with Django integration
- Factory Boy for test data generation (`UserFactory`)
- Allure reporting for comprehensive test reports
- Separate test files by functionality (products, comments, integration)

## Analytics and Data Science Features

The system includes sophisticated analytics capabilities:

**Sentiment Analysis**:
- Automatic sentiment scoring on review creation
- TextBlob integration for polarity analysis (-1 to 1 scale)
- Sentiment labels: positive, negative, neutral

**Trend Calculation**:
- Composite trend scoring based on views, reviews, ratings, sentiment
- Time-based trending analysis (daily, weekly, monthly)
- Weighted scoring algorithm in `calculate_trend_score()`

**Keywords Extraction**:
- TF-IDF vectorization for content analysis
- N-gram support for phrase extraction
- Stop word filtering and feature ranking

## API Authentication Patterns

**Token Authentication**:
```powershell
# Get token
curl -X POST http://localhost:8000/api-token-auth/ -d "username=admin&password=yourpassword"

# Use token in requests
curl -H "Authorization: Token your_token_here" http://localhost:8000/api/comments/
```

**Permission Levels**:
- Public: Product viewing, approved comments
- Authenticated: Comment creation, own data management
- Admin: Comment approval, analytics, all data access

## Database Considerations

**Key Relationships**:
- One review per user per product (`unique_together`)
- Soft approval system (boolean flags vs deletion)
- Hierarchical category → canonical → product structure

**Performance Features**:
- Pagination configured (20 items per page)
- Select/prefetch related optimization in querysets
- Aggregation queries for analytics calculations

## Testing Strategy

**Test Organization**:
- `conftest.py`: Shared fixtures and factories
- Separate files for different components
- Integration tests for complete workflows
- API endpoint testing with authentication scenarios

**Running Specific Tests**:
```powershell
# Test comment approval workflow
pytest tests/test_comments.py::TestCommentApproval

# Test with coverage
pytest --cov=myproject

# Test specific functionality
pytest -k "test_admin_approval"
```

## Common Development Scenarios

**Adding New Endpoints**:
1. Create/modify ViewSet in `views.py`
2. Add URL pattern in `urls.py`  
3. Create corresponding serializer
4. Add permissions if needed
5. Write tests

**Model Changes**:
1. Modify model in `models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Update serializers and views if needed
5. Update tests

**Analytics Extensions**:
- Extend `utils.py` for new analytics functions
- Use existing patterns for data aggregation
- Follow sentiment analysis patterns for ML integrations

## Dependencies and Tech Stack

**Core Framework**:
- Django 5.2+ with Django REST Framework
- SQLite for development (PostgreSQL ready)
- Token authentication

**Analytics Stack**:
- pandas, numpy for data processing
- scikit-learn for machine learning features
- TextBlob for sentiment analysis
- matplotlib, seaborn, plotly for visualization support

**Testing and Quality**:
- pytest with django integration
- Allure for advanced reporting
- Factory Boy for test data generation

This system is designed for extensibility and follows Django/DRF best practices with additional analytics and approval workflow capabilities.