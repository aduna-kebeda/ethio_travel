from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_packages = self.queryset.filter(featured=True, status='active')
        serializer = self.get_serializer(featured_packages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        package = self.get_object()
        reviews = package.reviews.all()
        serializer = PackageReviewSerializer(reviews, many=True)
        return Response(serializer.data)

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

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Package.objects.values_list('category', flat=True).distinct()
        return Response(categories)

    @action(detail=False, methods=['get'])
    def regions(self, request):
        regions = Package.objects.values_list('region', flat=True).distinct()
        return Response(regions)

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        package = self.get_object()
        package.featured = not package.featured
        package.save()
        return Response({'featured': package.featured})

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        package = self.get_object()
        package.status = 'draft' if package.status == 'active' else 'active'
        package.save()
        return Response({'status': package.status})

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        package = self.get_object()
        deleted, _ = SavedPackage.objects.filter(user=self.request.user, package=package).delete()
        if deleted:
            return Response({'message': 'Package removed from saved list'})
        return Response({'error': 'Package is not saved'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        saved_packages = SavedPackage.objects.filter(user=self.request.user)
        serializer = SavedPackageSerializer(saved_packages, many=True)
        return Response(serializer.data)

class PackageReviewViewSet(viewsets.ModelViewSet):
    queryset = PackageReview.objects.all()
    serializer_class = PackageReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    def perform_create(self, serializer):
        package = get_object_or_404(Package, pk=self.request.data.get('package'))
        if package.reviews.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You have already reviewed this package')
        serializer.save(package=package, user=self.request.user)

class DepartureViewSet(viewsets.ModelViewSet):
    queryset = Departure.objects.all()
    serializer_class = DepartureSerializer
    permission_classes = [IsAuthenticated, IsPackageOwnerOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(package__user=self.request.user)

    def perform_create(self, serializer):
        package = get_object_or_404(Package, pk=self.request.data.get('package'))
        if package.user != self.request.user and not self.request.user.is_staff:
            raise serializers.ValidationError('You can only add departures to your own packages')
        serializer.save(package=package)