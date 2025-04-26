from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogPostViewSet, BlogCommentViewSet,
    SavedPostViewSet
)

app_name = 'blog'

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='post')
router.register(r'comments', BlogCommentViewSet, basename='comment')
router.register(r'saved', SavedPostViewSet, basename='saved')

# Additional URL patterns that aren't covered by the ViewSet routes
urlpatterns = [
    path('', include(router.urls)),
    
    # Post related endpoints
    path('posts/featured/', BlogPostViewSet.as_view({'get': 'list'}), name='featured-posts'),
    path('posts/my_posts/', BlogPostViewSet.as_view({'get': 'list'}), name='my-posts'),
    path('posts/<int:pk>/toggle_featured/', BlogPostViewSet.as_view({'post': 'toggle_featured'}), name='toggle-featured'),
    path('posts/<int:pk>/view/', BlogPostViewSet.as_view({'post': 'view'}), name='view-post'),
    
    # Comment related endpoints
    path('posts/<int:post_pk>/comments/', BlogCommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments'),
    path('posts/<int:post_pk>/comments/<int:pk>/', BlogCommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='comment-detail'),
    path('posts/<int:post_pk>/comments/<int:pk>/report/', BlogCommentViewSet.as_view({'post': 'report'}), name='report-comment'),
    path('posts/<int:post_pk>/comments/<int:pk>/helpful/', BlogCommentViewSet.as_view({'post': 'mark_helpful'}), name='helpful-comment'),
    
    # Saved posts endpoints
    path('posts/<int:post_pk>/saved/', SavedPostViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-saved'),
    path('posts/<int:post_pk>/saved/<int:pk>/', SavedPostViewSet.as_view({
        'delete': 'destroy'
    }), name='saved-detail'),
    
    # Subscription endpoints (assuming you'll create these views later)
    path('subscriptions/', include([
        path('', BlogPostViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }), name='subscription-list'),
        path('<int:pk>/', BlogPostViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'
        }), name='subscription-detail'),
    ])),
]