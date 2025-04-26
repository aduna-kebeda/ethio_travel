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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = Business.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by business type
        business_type = self.request.query_params.get('business_type', None)
        if business_type:
            queryset = queryset.filter(business_type=business_type)
        
        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region=region)
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city=city)
        
        # Search by name or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Order by rating
        order_by = self.request.query_params.get('order_by', None)
        if order_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif order_by == 'date':
            queryset = queryset.order_by('-created_at')
        
        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_businesses = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_businesses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_businesses(self, request):
        my_businesses = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(my_businesses, many=True)
        return Response(serializer.data)

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

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None, business_pk=None):
        review = self.get_object()
        reason = request.data.get('reason', '')
        review.is_reported = True
        review.report_reason = reason
        review.save()
        return Response({"status": "review reported"})

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