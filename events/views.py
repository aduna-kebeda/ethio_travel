from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Event, EventReview, EventRegistration, SavedEvent, EventSubscription
from .serializers import (
    EventSerializer, EventListSerializer, EventDetailSerializer,
    EventReviewSerializer, EventRegistrationSerializer,
    SavedEventSerializer, EventSubscriptionSerializer
)
from .permissions import IsEventOwnerOrReadOnly, IsReviewOwnerOrReadOnly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'featured', 'status']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at', 'rating']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle_status']:
            return [IsAuthenticated(), IsEventOwnerOrReadOnly()]
        if self.action == 'toggle_featured':
            return [IsAdminUser()]
        return []

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(status='published')
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_events = self.queryset.filter(featured=True, status='published')
        serializer = self.get_serializer(featured_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        upcoming_events = self.queryset.filter(
            start_date__gt=timezone.now(),
            status='published'
        ).order_by('start_date')
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        events = self.queryset.filter(organizer=self.request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        event = self.get_object()
        reviews = event.reviews.all()
        sort_by = request.query_params.get('sort_by', 'newest')
        if sort_by == 'helpful':
            reviews = reviews.order_by('-helpful')
        else:
            reviews = reviews.order_by('-created_at')
        serializer = EventReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        event = self.get_object()
        if event.reviews.filter(user=self.request.user).exists():
            return Response(
                {'error': 'You have already reviewed this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EventReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event, user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        event = self.get_object()
        registrations = event.registrations.filter(status='confirmed')
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.status != 'published':
            return Response(
                {'error': 'This event is not available for registration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if event.capacity and event.current_attendees >= event.capacity:
            return Response(
                {'error': 'This event is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if event.registrations.filter(user=self.request.user).exists():
            return Response(
                {'error': 'You are already registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        registration = EventRegistration.objects.create(
            event=event, user=self.request.user, status='confirmed'
        )
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        registration = get_object_or_404(
            EventRegistration, event=event, user=self.request.user
        )
        registration.status = 'cancelled'
        registration.save()
        return Response({'message': 'Registration cancelled successfully'})

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        event = self.get_object()
        event.featured = not event.featured
        event.save()
        return Response({'featured': event.featured})

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        event = self.get_object()
        if event.status == 'draft':
            event.status = 'published'
        elif event.status == 'published':
            event.status = 'cancelled'
        event.save()
        return Response({'status': event.status})

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Event.objects.values_list('category', flat=True).distinct()
        return Response(categories)

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))
        
        start_date = timezone.datetime(year, month, 1)
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1)
        else:
            end_date = timezone.datetime(year, month + 1, 1)
        
        events = self.queryset.filter(
            start_date__gte=start_date,
            start_date__lt=end_date,
            status='published'
        ).values('id', 'title', 'start_date', 'category')
        
        # Group by date
        calendar_data = {}
        for event in events:
            date_str = event['start_date'].strftime('%Y-%m-%d')
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            calendar_data[date_str].append({
                'id': event['id'],
                'title': event['title'],
                'category': event['category']
            })
        
        return Response(calendar_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        event = self.get_object()
        if SavedEvent.objects.filter(user=self.request.user, event=event).exists():
            return Response(
                {'error': 'Event is already saved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        saved_event = SavedEvent.objects.create(user=self.request.user, event=event)
        serializer = SavedEventSerializer(saved_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        event = self.get_object()
        deleted, _ = SavedEvent.objects.filter(user=self.request.user, event=event).delete()
        if deleted:
            return Response({'message': 'Event removed from saved list'})
        return Response({'error': 'Event is not saved'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        saved_events = SavedEvent.objects.filter(user=self.request.user)
        serializer = SavedEventSerializer(saved_events, many=True)
        return Response(serializer.data)

class EventReviewViewSet(viewsets.ModelViewSet):
    queryset = EventReview.objects.all()
    serializer_class = EventReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.request.data.get('event'))
        if event.reviews.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You have already reviewed this event')
        serializer.save(event=event, user=self.request.user)

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

class SavedEventViewSet(viewsets.ModelViewSet):
    queryset = SavedEvent.objects.all()
    serializer_class = SavedEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.request.data.get('event'))
        if SavedEvent.objects.filter(user=self.request.user, event=event).exists():
            raise serializers.ValidationError('Event is already saved')
        serializer.save(user=self.request.user, event=event)

class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.request.data.get('event'))
        if event.status != 'published':
            raise serializers.ValidationError('This event is not available for registration')
        if event.capacity and event.current_attendees >= event.capacity:
            raise serializers.ValidationError('This event is full')
        if event.registrations.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You are already registered for this event')
        serializer.save(event=event, user=self.request.user, status='confirmed')

class EventSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = EventSubscription.objects.all()
    serializer_class = EventSubscriptionSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        categories = serializer.validated_data['categories']
        subscription, created = EventSubscription.objects.update_or_create(
            email=email, defaults={'categories': categories}
        )
        # Placeholder for email notification
        # send_notification_email(email, categories)
        return subscription