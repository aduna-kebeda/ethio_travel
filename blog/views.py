from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import BlogPost, BlogComment, SavedPost
from .serializers import (
    BlogPostSerializer, BlogCommentSerializer,
    SavedPostSerializer
)
from django.utils.text import slugify
from bson import ObjectId
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status', None)
        featured_param = self.request.query_params.get('featured', None)
        search_param = self.request.query_params.get('search', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if featured_param:
            featured = featured_param.lower() == 'true'
            queryset = queryset.filter(featured=featured)
        if search_param:
            queryset = queryset.filter(
                Q(title__icontains=search_param) |
                Q(content__icontains=search_param) |
                Q(excerpt__icontains=search_param) |
                Q(tags__name__icontains=search_param)
            ).distinct()
        return queryset

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Create a new blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the blog post'),
                'excerpt': openapi.Schema(type=openapi.TYPE_STRING, description='Short description of the blog post'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the blog post'),
                'authorName': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the author'),
                'authorImage': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL of author image'),
                'imageUrl': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL of blog post image'),
                'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of tags'),
                'featured': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False, description='Is this a featured post?'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'published'], default='draft', description='Post status')
            }
        ),
        responses={
            201: BlogPostSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="List all blog posts",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status (published/draft)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'featured',
                openapi.IN_QUERY,
                description="Filter by featured status",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'tags',
                openapi.IN_QUERY,
                description="Filter by tags (comma-separated)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={200: BlogPostSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Filter by status
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by featured
        featured = request.query_params.get('featured')
        if featured is not None:
            featured = featured.lower() == 'true'
            queryset = queryset.filter(featured=featured)
            
        # Filter by tags
        tags = request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__contains=tag_list)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Retrieve a specific blog post",
        responses={
            200: BlogPostSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Update a blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'excerpt': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
                'authorName': openapi.Schema(type=openapi.TYPE_STRING),
                'authorImage': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                'imageUrl': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'featured': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'published'])
            }
        ),
        responses={
            200: BlogPostSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Delete a blog post",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Get featured blog posts",
        responses={200: BlogPostSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = self.get_queryset().filter(featured=True, status='published')
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Blog Posts'],
        operation_description="Increment post views",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'views': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        post = self.get_object()
        post.views += 1
        post.save()
        return Response({'views': post.views})

class BlogCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BlogComment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        post = get_object_or_404(BlogPost, pk=self.kwargs['post_pk'])
        serializer.save(post=post, user=self.request.user)

    @swagger_auto_schema(
        tags=['Blog Comments'],
        operation_description="Create a new comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: BlogCommentSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Blog Comments'],
        operation_description="List all comments for a post",
        responses={200: BlogCommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class SavedPostViewSet(viewsets.ModelViewSet):
    serializer_class = SavedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedPost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Saved Posts'],
        operation_description="Save a blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['post'],
            properties={
                'post': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            201: SavedPostSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Saved Posts'],
        operation_description="List saved posts",
        responses={200: SavedPostSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Saved Posts'],
        operation_description="Remove a saved post",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)