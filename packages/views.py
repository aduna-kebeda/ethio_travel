from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Package, PackageReview, SavedPackage, Departure
from .serializers import (
    PackageSerializer, PackageListSerializer, PackageDetailSerializer,
    PackageReviewSerializer, SavedPackageSerializer, DepartureSerializer
)
from .permissions import IsPackageOwnerOrReadOnly, IsReviewOwnerOrReadOnly
from .filters import PackageFilter

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PackageFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PackageListSerializer
        elif self.action == 'retrieve':
            return PackageDetailSerializer
        return PackageSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'toggle_status', 'toggle_featured']:
            return [IsAuthenticated(), IsPackageOwnerOrReadOnly()]
        return []

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(status='active')
        return self.queryset

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Create a new tour package",
        responses={201: PackageSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="List all active tour packages",
        responses={200: PackageListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Retrieve details of a specific tour package",
        responses={200: PackageDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Update a tour package",
        responses={200: PackageSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Delete a tour package",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Get featured tour packages",
        responses={200: PackageListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_packages = self.queryset.filter(featured=True, status='active')
        serializer = self.get_serializer(featured_packages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Get all reviews for a specific package",
        responses={200: PackageReviewSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        package = self.get_object()
        reviews = package.reviews.all()
        serializer = PackageReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Add a review to a package",
        request_body=PackageReviewSerializer,
        responses={
            201: PackageReviewSerializer,
            400: "Bad request - Review already exists"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        package = self.get_object()
        if package.reviews.filter(user=self.request.user).exists():
            return Response(
                {'error': 'You have already reviewed this package'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PackageReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(package=package, user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Get list of all package categories",
        responses={200: openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))}
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Package.objects.values_list('category', flat=True).distinct()
        return Response(categories)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Get list of all package regions",
        responses={200: openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))}
    )
    @action(detail=False, methods=['get'])
    def regions(self, request):
        regions = Package.objects.values_list('region', flat=True).distinct()
        return Response(regions)

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Toggle featured status of a package",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'featured': openapi.Schema(type=openapi.TYPE_BOOLEAN)})}
    )
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        package = self.get_object()
        package.featured = not package.featured
        package.save()
        return Response({'featured': package.featured})

    @swagger_auto_schema(
        tags=['Tour Packages'],
        operation_description="Toggle active/draft status of a package",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})}
    )
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        package = self.get_object()
        package.status = 'draft' if package.status == 'active' else 'active'
        package.save()
        return Response({'status': package.status})

    @swagger_auto_schema(
        tags=['Saved Packages'],
        operation_description="Save a package for later",
        responses={
            201: SavedPackageSerializer,
            400: "Bad request - Package already saved"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        package = self.get_object()
        saved_package, created = SavedPackage.objects.get_or_create(
            user=self.request.user, package=package
        )
        if not created:
            return Response({'error': 'Package is already saved'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SavedPackageSerializer(saved_package)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=['Saved Packages'],
        operation_description="Remove a package from saved list",
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}),
            400: "Bad request - Package not saved"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        package = self.get_object()
        deleted, _ = SavedPackage.objects.filter(user=self.request.user, package=package).delete()
        if deleted:
            return Response({'message': 'Package removed from saved list'})
        return Response({'error': 'Package is not saved'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Saved Packages'],
        operation_description="Get list of saved packages for the current user",
        responses={200: SavedPackageSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        saved_packages = SavedPackage.objects.filter(user=self.request.user)
        serializer = SavedPackageSerializer(saved_packages, many=True)
        return Response(serializer.data)

class PackageReviewViewSet(viewsets.ModelViewSet):
    queryset = PackageReview.objects.all()
    serializer_class = PackageReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Create a new package review",
        responses={201: PackageReviewSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="List all package reviews",
        responses={200: PackageReviewSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Retrieve a specific package review",
        responses={200: PackageReviewSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Update a package review",
        responses={200: PackageReviewSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Reviews'],
        operation_description="Delete a package review",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        package = get_object_or_404(Package, pk=self.request.data.get('package'))
        if package.reviews.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You have already reviewed this package')
        serializer.save(package=package, user=self.request.user)

class DepartureViewSet(viewsets.ModelViewSet):
    queryset = Departure.objects.all()
    serializer_class = DepartureSerializer
    permission_classes = [IsAuthenticated, IsPackageOwnerOrReadOnly]

    @swagger_auto_schema(
        tags=['Package Departures'],
        operation_description="Create a new departure date for a package",
        responses={201: DepartureSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Departures'],
        operation_description="List all departure dates for user's packages",
        responses={200: DepartureSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Departures'],
        operation_description="Retrieve a specific departure date",
        responses={200: DepartureSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Departures'],
        operation_description="Update a departure date",
        responses={200: DepartureSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Package Departures'],
        operation_description="Delete a departure date",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(package__user=self.request.user)

    def perform_create(self, serializer):
        package = get_object_or_404(Package, pk=self.request.data.get('package'))
        if package.user != self.request.user and not self.request.user.is_staff:
            raise serializers.ValidationError('You can only add departures to your own packages')
        serializer.save(package=package)