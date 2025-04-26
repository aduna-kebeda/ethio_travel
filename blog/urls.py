from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogPostViewSet, BlogCommentViewSet,
    SavedPostViewSet
)

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)
router.register(r'comments', BlogCommentViewSet, basename='comment')
router.register(r'saved', SavedPostViewSet, basename='saved')

urlpatterns = [
    path('', include(router.urls)),
]

# Available endpoints:
# GET /api/blog/categories/ - List all categories
# POST /api/blog/categories/ - Create a new category
# GET /api/blog/categories/{id}/ - Retrieve a specific category
# PUT /api/blog/categories/{id}/ - Update a specific category
# DELETE /api/blog/categories/{id}/ - Delete a specific category
# GET /api/blog/posts/ - List all blog posts
# POST /api/blog/posts/ - Create a new blog post
# GET /api/blog/posts/{id}/ - Retrieve a specific blog post
# PUT /api/blog/posts/{id}/ - Update a specific blog post
# DELETE /api/blog/posts/{id}/ - Delete a specific blog post
# GET /api/blog/posts/featured/ - List featured posts
# GET /api/blog/posts/my_posts/ - List user's posts
# POST /api/blog/posts/{id}/toggle_featured/ - Toggle featured status (staff only)
# GET /api/blog/posts/{post_pk}/comments/ - List comments for a post
# POST /api/blog/posts/{post_pk}/comments/ - Create a comment for a post
# GET /api/blog/posts/{post_pk}/comments/{id}/ - Retrieve a specific comment
# PUT /api/blog/posts/{post_pk}/comments/{id}/ - Update a specific comment
# DELETE /api/blog/posts/{post_pk}/comments/{id}/ - Delete a specific comment
# POST /api/blog/posts/{post_pk}/comments/{id}/report/ - Report a comment
# POST /api/blog/posts/{post_pk}/comments/{id}/helpful/ - Mark a comment as helpful
# GET /api/blog/posts/{post_pk}/saved/ - List saved posts for a user
# POST /api/blog/posts/{post_pk}/saved/ - Save a post
# DELETE /api/blog/posts/{post_pk}/saved/{id}/ - Remove a saved post
# GET /api/blog/subscriptions/ - List all subscriptions
# POST /api/blog/subscriptions/ - Create a new subscription
# GET /api/blog/subscriptions/{id}/ - Retrieve a specific subscription
# PUT /api/blog/subscriptions/{id}/ - Update a specific subscription
# DELETE /api/blog/subscriptions/{id}/ - Delete a specific subscription 