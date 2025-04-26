from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Destination, DestinationReview, SavedDestination
from .serializers import (
    DestinationSerializer, DestinationDetailSerializer,
    DestinationReviewSerializer, SavedDestinationSerializer
)
from .permissions import IsDestinationOwnerOrReadOnly, IsReviewOwnerOrReadOnly

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'region', 'city', 'featured', 'status']
    search_fields = ['title', 'description', 'city']
    ordering_fields = ['rating', 'review_count', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DestinationDetailSerializer
        return DestinationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'toggle_featured', 'toggle_status']:
            return [IsAuthenticated(), IsDestinationOwnerOrReadOnly()]
        return []

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(status='active')
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        destination = self.get_object()
        if destination.reviews.filter(user=request.user).exists():
            return Response(
                {'error': 'You have already reviewed this destination'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DestinationReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(destination=destination, user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        destination = self.get_object()
        reviews = destination.reviews.all()
        sort_by = request.query_params.get('sort_by', 'created_at')
        if sort_by in ['rating', 'helpful', 'created_at']:
            reviews = reviews.order_by(f'-{sort_by}')
        serializer = DestinationReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        destination = self.get_object()
        destination.featured = not destination.featured
        destination.save()
        return Response({'featured': destination.featured})

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        destination = self.get_object()
        destination.status = 'draft' if destination.status == 'active' else 'active'
        destination.save()
        return Response({'status': destination.status})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        destination = self.get_object()
        saved_destination, created = SavedDestination.objects.get_or_create(
            user=self.request.user, destination=destination
        )
        if not created:
            return Response({'error': 'Destination is already saved'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SavedDestinationSerializer(saved_destination)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        destination = self.get_object()
        deleted, _ = SavedDestination.objects.filter(user=self.request.user, destination=destination).delete()
        if deleted:
            return Response({'message': 'Destination removed from saved list'})
        return Response({'error': 'Destination is not saved'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        saved_destinations = SavedDestination.objects.filter(user=self.request.user)
        serializer = SavedDestinationSerializer(saved_destinations, many=True)
        return Response(serializer.data)

class DestinationReviewViewSet(viewsets.ModelViewSet):
    queryset = DestinationReview.objects.all()
    serializer_class = DestinationReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    def perform_create(self, serializer):
        destination = get_object_or_404(Destination, pk=self.request.data.get('destination'))
        if destination.reviews.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You have already reviewed this destination')
        serializer.save(destination=destination, user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful += 1
        review.save()
        return Response({'helpful': review.helpful})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        review = self.get_object()
        review.reported = True
        review.save()
        return Response({'message': 'Review reported successfully'})

class SavedDestinationViewSet(viewsets.ModelViewSet):
    queryset = SavedDestination.objects.all()
    serializer_class = SavedDestinationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        destination = get_object_or_404(Destination, pk=self.request.data.get('destination'))
        if SavedDestination.objects.filter(user=self.request.user, destination=destination).exists():
            raise serializers.ValidationError('Destination is already saved')
        serializer.save(user=self.request.user, destination=destination)