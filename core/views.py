from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.urls import NoReverseMatch

@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root View
    """
    return Response({
        'authentication': {
            'register': {
                'url': reverse('users:user-register', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Register a new user',
                'body': {
                    'username': 'string',
                    'email': 'string',
                    'password': 'string',
                    'password2': 'string',
                    'first_name': 'string',
                    'last_name': 'string',
                    'role': 'string (user, business_owner, admin)'
                }
            },
            'login': {
                'url': reverse('token_obtain_pair', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Get JWT access token',
                'body': {
                    'email': 'string',
                    'password': 'string'
                }
            },
            'refresh': {
                'url': reverse('token_refresh', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Refresh JWT access token',
                'body': {
                    'refresh': 'string (JWT refresh token)'
                },
                'response': {
                    'access': 'string (new JWT token)'
                }
            }
        },
        'email_verification': {
            'verify': {
                'url': reverse('users:user-verify-email', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Verify user email with verification code',
                'body': {
                    'email': 'string',
                    'code': 'string (6-digit code)'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            },
            'resend': {
                'url': reverse('users:user-resend-verification', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Resend verification code to email',
                'body': {
                    'email': 'string'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            }
        },
        'password_management': {
            'forgot': {
                'url': reverse('users:user-forgot-password', request=request, format=format),
                'method': 'POST',
                'auth_required': False,
                'description': 'Request password reset link',
                'body': {
                    'email': 'string'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            },
            'reset': {
                'url': '/api/users/reset_password/{token}/',
                'method': 'POST',
                'auth_required': False,
                'description': 'Reset password using reset token',
                'body': {
                    'new_password': 'string (min length: 8)',
                    'new_password2': 'string (must match new_password)'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            },
            'change': {
                'url': reverse('users:user-change-password', request=request, format=format),
                'method': 'POST',
                'auth_required': True,
                'description': 'Change password while logged in',
                'body': {
                    'current_password': 'string',
                    'new_password': 'string (min length: 8)',
                    'new_password2': 'string (must match new_password)'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            }
        },
        'profile_management': {
            'me': {
                'url': reverse('users:user-me', request=request, format=format),
                'method': 'GET',
                'auth_required': True,
                'description': 'Get current user profile details',
                'response': {
                    'username': 'string',
                    'email': 'string',
                    'first_name': 'string',
                    'last_name': 'string',
                    'role': 'string',
                    'status': 'string',
                    'email_verified': 'boolean',
                    'image': 'string (url)'
                }
            },
            'change_email': {
                'url': reverse('users:user-change-email', request=request, format=format),
                'method': 'POST',
                'auth_required': True,
                'description': 'Change email address (requires verification)',
                'body': {
                    'email': 'string',
                    'password': 'string'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            },
            'logout': {
                'url': reverse('users:user-logout', request=request, format=format),
                'method': 'POST',
                'auth_required': True,
                'description': 'Logout and invalidate refresh token',
                'body': {
                    'refresh_token': 'string'
                },
                'response': {
                    'status': 'string (success/error)',
                    'message': 'string'
                }
            }
        },
        'admin': {
            'users': {
                'list': {
                    'url': reverse('users:user-list', request=request, format=format),
                    'method': 'GET',
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'List all users',
                    'query_params': {
                        'page': 'integer',
                        'page_size': 'integer',
                        'search': 'string'
                    }
                },
                'detail': {
                    'url': '/api/users/management/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'Manage individual user',
                    'path_params': {
                        'id': 'integer'
                    }
                },
                'toggle_active': {
                    'url': '/api/users/management/{id}/toggle_active/',
                    'method': 'POST',
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'Toggle user active status',
                    'path_params': {
                        'id': 'integer'
                    }
                },
                'toggle_staff': {
                    'url': '/api/users/management/{id}/toggle_staff/',
                    'method': 'POST',
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'Toggle user staff status',
                    'path_params': {
                        'id': 'integer'
                    }
                }
            },
            'profiles': {
                'list': {
                    'url': reverse('users:profile-list', request=request, format=format),
                    'method': 'GET',
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'List all user profiles',
                    'query_params': {
                        'page': 'integer',
                        'page_size': 'integer'
                    }
                },
                'detail': {
                    'url': '/api/users/profiles/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'Manage individual profile',
                    'path_params': {
                        'id': 'integer'
                    }
                }
            },
            'business_profiles': {
                'list': {
                    'url': reverse('users:business-profile-list', request=request, format=format),
                    'method': 'GET',
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'List all business profiles',
                    'query_params': {
                        'page': 'integer',
                        'page_size': 'integer'
                    }
                },
                'detail': {
                    'url': '/api/users/business_profiles/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'auth_required': True,
                    'admin_required': True,
                    'description': 'Manage individual business profile',
                    'path_params': {
                        'id': 'integer'
                    }
                }
            }
        },
        'destinations': {
            'list': {
                'url': reverse('destinations:destination-list', request=request, format=format),
                'method': 'GET',
                'auth_required': False,
                'description': 'List all destinations',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'search': 'string'
                }
            }
        },
        'events': {
            'list': {
                'url': reverse('events:event-list', request=request, format=format),
                'method': 'GET',
                'auth_required': False,
                'description': 'List all events',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'search': 'string'
                }
            }
        },
        'packages': {
            'list': {
                'url': reverse('packages:package-list', request=request, format=format),
                'method': 'GET',
                'auth_required': False,
                'description': 'List all travel packages',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'search': 'string'
                }
            }
        },
        'business': {
            'list': {
                'url': '/api/business/',
                'method': 'GET',
                'auth_required': False,
                'description': 'List all businesses',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'search': 'string',
                    'business_type': 'string',
                    'region': 'string',
                    'city': 'string'
                }
            },
            'create': {
                'url': '/api/business/create/',
                'method': 'POST',
                'auth_required': True,
                'description': 'Create a new business',
                'body': {
                    'business_name': 'string (required)',
                    'business_type': 'string (required)',
                    'description': 'string (required)',
                    'short_description': 'string (required)',
                    'region': 'string (required)',
                    'city': 'string (required)',
                    'address': 'string (required)',
                    'phone': 'string (required)',
                    'email': 'string (required)',
                    'website': 'string (optional)',
                    'image': 'string (optional)',
                    'gallery_images': 'array (optional)',
                    'opening_hours': 'array (optional)',
                    'facilities': 'array (optional)',
                    'services': 'array (optional)',
                    'team': 'array (optional)',
                    'facebook': 'string (optional)',
                    'instagram': 'string (optional)',
                    'coordinates': 'array (optional)'
                }
            },
            'detail': {
                'url': '/api/business/{id}/',
                'method': 'GET',
                'auth_required': False,
                'description': 'Get business details',
                'path_params': {
                    'id': 'integer'
                }
            },
            'reviews': {
                'url': '/api/business/{id}/reviews/',
                'method': 'GET',
                'auth_required': False,
                'description': 'List business reviews',
                'path_params': {
                    'id': 'integer'
                }
            },
            'add_review': {
                'url': '/api/business/{id}/add_review/',
                'method': 'POST',
                'auth_required': True,
                'description': 'Add a review to a business',
                'path_params': {
                    'id': 'integer'
                },
                'body': {
                    'rating': 'number (1-5)',
                    'comment': 'string'
                }
            },
            'my_businesses': {
                'url': '/api/business/my-businesses/',
                'method': 'GET',
                'auth_required': True,
                'description': 'List businesses owned by the current user'
            },
            'featured': {
                'url': '/api/business/featured/',
                'method': 'GET',
                'auth_required': False,
                'description': 'List featured businesses'
            }
        },
        'blog': {
            'list': {
                'url': reverse('blog:post-list', request=request, format=format),
                'method': 'GET',
                'auth_required': False,
                'description': 'List all blog posts',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'search': 'string',
                    'status': 'string (published/draft)',
                    'featured': 'boolean'
                }
            },
            'create': {
                'url': reverse('blog:post-list', request=request, format=format),
                'method': 'POST',
                'auth_required': True,
                'description': 'Create a new blog post',
                'body': {
                    'title': 'string',
                    'content': 'string',
                    'excerpt': 'string (optional)',
                    'featured_image': 'file (optional)',
                    'tags': 'array of strings',
                    'status': 'string (draft/published)'
                }
            }
        },
        'booking': {
            'list': {
                'url': reverse('booking:booking-list', request=request, format=format),
                'method': 'GET',
                'auth_required': True,
                'description': 'List user bookings',
                'query_params': {
                    'page': 'integer',
                    'page_size': 'integer',
                    'status': 'string'
                }
            },
            'create': {
                'url': reverse('booking:booking-list', request=request, format=format),
                'method': 'POST',
                'auth_required': True,
                'description': 'Create new booking'
            }
        }
    })

class APIRootView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            "authentication": {
                "register": {
                    "url": reverse("users:register", request=request),
                    "method": "POST",
                    "auth_required": False,
                    "description": "Register a new user",
                    "body": {
                        "username": "string",
                        "email": "string",
                        "password": "string",
                        "password2": "string",
                        "first_name": "string",
                        "last_name": "string",
                        "role": "string (user, business_owner, admin)"
                    }
                },
                "login": {
                    "url": reverse("token_obtain_pair", request=request),
                    "method": "POST",
                    "auth_required": False,
                    "description": "Get JWT access token",
                    "body": {
                        "email": "string",
                        "password": "string"
                    },
                    "response": {
                        "access": "string (JWT token)",
                        "refresh": "string (JWT refresh token)"
                    }
                }
            },
            "blog": {
                "list": {
                    "url": reverse("blog:post-list", request=request),
                    "method": "GET",
                    "auth_required": False,
                    "description": "List all blog posts",
                    "query_params": {
                        "page": "integer",
                        "page_size": "integer",
                        "search": "string",
                        "status": "string (published/draft)",
                        "featured": "boolean"
                    }
                },
                "create": {
                    "url": reverse("blog:post-list", request=request),
                    "method": "POST",
                    "auth_required": True,
                    "description": "Create a new blog post",
                    "body": {
                        "title": "string",
                        "content": "string",
                        "excerpt": "string (optional)",
                        "featured_image": "file (optional)",
                        "tags": "array of strings",
                        "status": "string (draft/published)"
                    }
                }
            },
            "businesses": {
                "list": {
                    "url": reverse("businesses:business-list", request=request),
                    "method": "GET",
                    "auth_required": False,
                    "description": "List all businesses",
                    "query_params": {
                        "page": "integer",
                        "page_size": "integer",
                        "search": "string",
                        "business_type": "string",
                        "verified": "boolean",
                        "status": "string"
                    }
                },
                "create": {
                    "url": reverse("businesses:business-create", request=request),
                    "method": "POST",
                    "auth_required": True,
                    "description": "Create a new business",
                    "body": {
                        "business_name": "string",
                        "business_type": "string",
                        "description": "string",
                        "short_description": "string",
                        "region": "string",
                        "city": "string",
                        "address": "string",
                        "phone": "string",
                        "email": "string",
                        "website": "string (optional)",
                        "image": "string (optional)",
                        "gallery_images": "array (optional)",
                        "opening_hours": "array (optional)",
                        "facilities": "array (optional)",
                        "services": "array (optional)",
                        "team": "array (optional)",
                        "facebook": "string (optional)",
                        "instagram": "string (optional)",
                        "coordinates": "array (optional)"
                    }
                },
                "reviews": {
                    "url": reverse("businesses:review-list", request=request),
                    "method": "GET",
                    "auth_required": False,
                    "description": "List all business reviews"
                }
            }
        }
        return Response(data) 