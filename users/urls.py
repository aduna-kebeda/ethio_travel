from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProfileViewSet, BusinessProfileViewSet
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes

app_name = 'users'

# Create a router and register our viewsets with it
router = DefaultRouter()

# The API URLs are determined by explicit URL patterns
urlpatterns = [
    # Authentication endpoints
    path('login/', UserViewSet.as_view({'post': 'login', 'get': 'login'}), name='user-login'),
    path('register/', UserViewSet.as_view({'post': 'register', 'get': 'register'}), name='user-register'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='user-logout'),
    
    # Email verification endpoints
    path('verify_email/', UserViewSet.as_view({'post': 'verify_email'}), name='user-verify-email'),
    path('resend_verification/', UserViewSet.as_view({'post': 'resend_verification'}), name='user-resend-verification'),
    path('change_email/', UserViewSet.as_view({'post': 'change_email'}), name='user-change-email'),
    
    # Password management endpoints
    path('forgot_password/', UserViewSet.as_view({'post': 'forgot_password'}), name='user-forgot-password'),
    path('reset_password/<str:token>/', UserViewSet.as_view({'post': 'reset_password'}), name='user-reset-password'),
    path('change_password/', UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    
    # User profile endpoint
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    
    # Admin management endpoints
    path('management/', include([
        path('', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
        path('<int:pk>/', UserViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), name='user-detail'),
        path('<int:pk>/toggle_active/', UserViewSet.as_view({'post': 'toggle_active'}), name='user-toggle-active'),
        path('<int:pk>/toggle_staff/', UserViewSet.as_view({'post': 'toggle_staff'}), name='user-toggle-staff'),
    ])),
    
    # Profile management
    path('profiles/', include([
        path('', ProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='profile-list'),
        path('<int:pk>/', ProfileViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), name='profile-detail'),
    ])),
    
    # Business profile management
    path('business_profiles/', include([
        path('', BusinessProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='business-profile-list'),
        path('<int:pk>/', BusinessProfileViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), name='business-profile-detail'),
    ])),
]

"""
API Endpoints Documentation:

Authentication:
-------------
POST /api/users/register/
    Register a new user
    Body: {username, email, password, password2, first_name, last_name, role}

POST /api/users/login/
    Login user
    Body: {email, password}

POST /api/users/logout/
    Logout user (requires authentication)
    Body: {refresh_token}

Email Management:
---------------
POST /api/users/verify_email/
    Verify email address
    Body: {email, code}

POST /api/users/resend_verification/
    Resend verification code
    Body: {email}

POST /api/users/change_email/
    Change email address (requires authentication)
    Body: {email, password}

Password Management:
-----------------
POST /api/users/forgot_password/
    Request password reset
    Body: {email}

POST /api/users/reset_password/{token}/
    Reset password using token
    Body: {new_password, new_password2}

POST /api/users/change_password/
    Change password (requires authentication)
    Body: {current_password, new_password, new_password2}

User Profile:
-----------
GET /api/users/me/
    Get current user profile (requires authentication)

Admin Management (requires admin access):
-------------------------------------
GET    /api/users/management/
POST   /api/users/management/
GET    /api/users/management/{id}/
PUT    /api/users/management/{id}/
PATCH  /api/users/management/{id}/
DELETE /api/users/management/{id}/
POST   /api/users/management/{id}/toggle_active/
POST   /api/users/management/{id}/toggle_staff/

Profile Management:
----------------
GET    /api/users/profiles/
POST   /api/users/profiles/
GET    /api/users/profiles/{id}/
PUT    /api/users/profiles/{id}/
PATCH  /api/users/profiles/{id}/
DELETE /api/users/profiles/{id}/

Business Profile Management:
------------------------
GET    /api/users/business_profiles/
POST   /api/users/business_profiles/
GET    /api/users/business_profiles/{id}/
PUT    /api/users/business_profiles/{id}/
PATCH  /api/users/business_profiles/{id}/
DELETE /api/users/business_profiles/{id}/
"""