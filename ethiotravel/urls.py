"""
URL configuration for ethiotravel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import api_root
from django.views.generic import RedirectView

# Main URL patterns
urlpatterns = [
    # API Root
    path('', api_root, name='api-root'),
    path('api/', RedirectView.as_view(url='/', permanent=False), name='api-redirect'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),  # Django REST framework browsable API auth
    
    # API endpoints with browsable API support
    path('api/users/', include('users.urls')),
    path('api/destinations/', include('destinations.urls')),
    path('api/events/', include('events.urls')),
    path('api/business/', include('business.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/booking/', include('booking.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Available endpoints:
# GET / - API root with all available endpoints
# POST /api/token/ - Get JWT access token
# POST /api/token/refresh/ - Refresh JWT access token
# POST /api/users/register/ - Register a new user
# POST /api/users/verify-email/ - Verify user email
# POST /api/users/forgot-password/ - Request password reset
# POST /api/users/reset-password/ - Reset password with token
# POST /api/users/change-password/ - Change password (authenticated)
# POST /api/users/change-email/ - Change email (authenticated)
# GET /api/users/me/ - Get current user profile (authenticated)
# POST /api/users/logout/ - Logout user (authenticated)
# GET /api/users/ - List users (admin only)
# GET /api/users/{id}/ - Get user details (admin only)
# PUT /api/users/{id}/ - Update user (admin only)
# DELETE /api/users/{id}/ - Delete user (admin only)
# POST /api/users/{id}/toggle-active/ - Toggle user active status (admin only)
# POST /api/users/{id}/toggle-staff/ - Toggle user staff status (admin only)
# GET /api/profiles/ - List profiles (authenticated)
# GET /api/profiles/{id}/ - Get profile details (authenticated)
# PUT /api/profiles/{id}/ - Update profile (owner only)
# GET /api/business-profiles/ - List business profiles (authenticated)
# GET /api/business-profiles/{id}/ - Get business profile details (authenticated)
# PUT /api/business-profiles/{id}/ - Update business profile (owner only)
# GET /api/destinations/ - List destinations
# GET /api/destinations/{id}/ - Get destination details
# GET /api/events/ - List events
# GET /api/events/{id}/ - Get event details
# GET /api/business/ - List businesses
# GET /api/business/{id}/ - Get business details
# GET /api/blog/ - List blog posts
# GET /api/blog/{id}/ - Get blog post details
# GET /api/packages/ - List travel packages
# GET /api/packages/{id}/ - Get package details
# GET /api/booking/ - List bookings (authenticated)
# GET /api/booking/{id}/ - Get booking details (authenticated)
# POST /api/booking/ - Create booking (authenticated)
# PUT /api/booking/{id}/ - Update booking (authenticated)
# DELETE /api/booking/{id}/ - Cancel booking (authenticated)
