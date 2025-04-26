from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, BusinessReviewViewSet, SavedBusinessViewSet

app_name = 'business'

# Create a router and register our viewsets with it
router = DefaultRouter()

# The API URLs are determined by explicit URL patterns
urlpatterns = [
    # Business management
    path('businesses/', BusinessViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='business-list'),
    path('businesses/<int:pk>/', BusinessViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='business-detail'),
    
    # Business actions
    path('businesses/featured/', BusinessViewSet.as_view({'get': 'featured'}), name='business-featured'),
    path('businesses/my-businesses/', BusinessViewSet.as_view({'get': 'my_businesses'}), name='my-businesses'),
    path('businesses/<int:pk>/toggle-featured/', BusinessViewSet.as_view({'post': 'toggle_featured'}), name='business-toggle-featured'),
    path('businesses/<int:pk>/verify/', BusinessViewSet.as_view({'post': 'verify'}), name='business-verify'),
    
    # Business reviews
    path('businesses/<int:business_pk>/reviews/', BusinessReviewViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='business-review-list'),
    path('businesses/<int:business_pk>/reviews/<int:pk>/', BusinessReviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='business-review-detail'),
    path('businesses/<int:business_pk>/reviews/<int:pk>/report/', BusinessReviewViewSet.as_view({'post': 'report'}), name='business-review-report'),
    path('businesses/<int:business_pk>/reviews/<int:pk>/helpful/', BusinessReviewViewSet.as_view({'post': 'helpful'}), name='business-review-helpful'),
    
    # Saved businesses
    path('businesses/<int:business_pk>/saved/', SavedBusinessViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='saved-business-list'),
    path('businesses/<int:business_pk>/saved/<int:pk>/', SavedBusinessViewSet.as_view({
        'delete': 'destroy'
    }), name='saved-business-detail'),
]

# Available endpoints:
# GET /api/business/businesses/ - List all businesses
# POST /api/business/businesses/ - Create a new business
# GET /api/business/businesses/{id}/ - Retrieve a specific business
# PUT /api/business/businesses/{id}/ - Update a specific business
# PATCH /api/business/businesses/{id}/ - Partially update a specific business
# DELETE /api/business/businesses/{id}/ - Delete a specific business
# GET /api/business/businesses/featured/ - List featured businesses
# GET /api/business/businesses/my_businesses/ - List user's businesses
# POST /api/business/businesses/{id}/toggle_featured/ - Toggle featured status (admin only)
# POST /api/business/businesses/{id}/verify/ - Verify a business (admin only)
# GET /api/business/businesses/{business_pk}/reviews/ - List reviews for a business
# POST /api/business/businesses/{business_pk}/reviews/ - Create a review for a business
# GET /api/business/businesses/{business_pk}/reviews/{id}/ - Retrieve a specific review
# PUT /api/business/businesses/{business_pk}/reviews/{id}/ - Update a specific review
# DELETE /api/business/businesses/{business_pk}/reviews/{id}/ - Delete a specific review
# POST /api/business/businesses/{business_pk}/reviews/{id}/report/ - Report a review
# POST /api/business/businesses/{business_pk}/reviews/{id}/helpful/ - Mark a review as helpful
# GET /api/business/businesses/{business_pk}/saved/ - List saved businesses for a user
# POST /api/business/businesses/{business_pk}/saved/ - Save a business
# DELETE /api/business/businesses/{business_pk}/saved/{id}/ - Remove a saved business 