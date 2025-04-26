from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Business, BusinessReview, SavedBusiness
from .serializers import (
    BusinessListSerializer, BusinessDetailSerializer, BusinessCreateSerializer,
    BusinessReviewSerializer, BusinessReviewCreateSerializer, SavedBusinessSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return BusinessDetailSerializer
        return BusinessListSerializer

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Create a new business",
        request_body=BusinessCreateSerializer,
        responses={
            201: BusinessDetailSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        if request.method == 'GET':
            return Response({
                'message': 'Please provide the following information to create a business',
                'fields': {
                    'name': 'string (required)',
                    'business_type': 'string (required)',
                    'description': 'string',
                    'contact_email': 'string',
                    'contact_phone': 'string',
                    'website': 'string',
                    'region': 'string',
                    'city': 'string',
                    'address': 'string',
                    'latitude': 'float',
                    'longitude': 'float',
                    'main_image': 'file',
                    'gallery_images': 'array of files',
                    'social_media_links': 'object',
                    'opening_hours': 'string',
                    'facilities': 'array of strings',
                    'services': 'array of strings',
                    'team': 'array of objects'
                }
            })
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="List all businesses",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by status"),
            openapi.Parameter('business_type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by business type"),
            openapi.Parameter('region', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by region"),
            openapi.Parameter('city', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by city"),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Search by name or description"),
            openapi.Parameter('order_by', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Order by rating or date")
        ],
        responses={
            200: BusinessListSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Retrieve a business",
        responses={
            200: BusinessDetailSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Update a business",
        request_body=BusinessDetailSerializer,
        responses={
            200: BusinessDetailSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Delete a business",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="List featured businesses",
        responses={
            200: BusinessListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_businesses = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_businesses, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="List user's businesses",
        responses={
            200: BusinessListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def my_businesses(self, request):
        my_businesses = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(my_businesses, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Toggle business featured status",
        responses={
            200: openapi.Response(
                description="Featured status toggled",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_featured': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            403: "Forbidden"
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        business = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can feature businesses."},
                status=status.HTTP_403_FORBIDDEN
            )
        business.is_featured = not business.is_featured
        business.save()
        return Response({"is_featured": business.is_featured})

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Verify a business",
        responses={
            200: openapi.Response(
                description="Business verified",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            403: "Forbidden"
        }
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        business = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can verify businesses."},
                status=status.HTTP_403_FORBIDDEN
            )
        business.is_verified = True
        business.save()
        return Response({"is_verified": True})

class BusinessReviewViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BusinessReview.objects.filter(business_id=self.kwargs['business_pk'])

    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessReviewCreateSerializer
        return BusinessReviewSerializer

    def perform_create(self, serializer):
        business = get_object_or_404(Business, pk=self.kwargs['business_pk'])
        serializer.save(business=business)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Create a business review",
        request_body=BusinessReviewCreateSerializer,
        responses={
            201: BusinessReviewSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="List business reviews",
        responses={
            200: BusinessReviewSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Report a review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Review reported",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None, business_pk=None):
        review = self.get_object()
        reason = request.data.get('reason', '')
        review.is_reported = True
        review.report_reason = reason
        review.save()
        return Response({"status": "review reported"})

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Mark review as helpful",
        responses={
            200: openapi.Response(
                description="Helpful votes updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'helpful_votes': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None, business_pk=None):
        review = self.get_object()
        review.helpful_votes += 1
        review.save()
        return Response({"helpful_votes": review.helpful_votes})

class SavedBusinessViewSet(viewsets.ModelViewSet):
    serializer_class = SavedBusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedBusiness.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        business = get_object_or_404(Business, pk=self.kwargs['business_pk'])
        serializer.save(user=self.request.user, business=business)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="Save a business",
        responses={
            201: SavedBusinessSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Business'],
        operation_description="List saved businesses",
        responses={
            200: SavedBusinessSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs) 