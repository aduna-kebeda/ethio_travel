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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Create a new event",
        request_body=EventSerializer,
        responses={
            201: EventSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List all published events",
        responses={
            200: EventListSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Retrieve event details",
        responses={
            200: EventDetailSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Update event details",
        request_body=EventSerializer,
        responses={
            200: EventSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Delete an event",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List featured events",
        responses={
            200: EventListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_events = self.queryset.filter(featured=True, status='published')
        serializer = self.get_serializer(featured_events, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List upcoming events",
        responses={
            200: EventListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        upcoming_events = self.queryset.filter(
            start_date__gt=timezone.now(),
            status='published'
        ).order_by('start_date')
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List events organized by the current user",
        responses={
            200: EventListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def my_events(self, request):
        events = self.queryset.filter(organizer=self.request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List reviews for an event",
        manual_parameters=[
            openapi.Parameter(
                'sort_by',
                openapi.IN_QUERY,
                description="Sort reviews by 'newest' or 'helpful'",
                type=openapi.TYPE_STRING,
                enum=['newest', 'helpful']
            )
        ],
        responses={
            200: EventReviewSerializer(many=True)
        }
    )
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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Add a review to an event",
        request_body=EventReviewSerializer,
        responses={
            201: EventReviewSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List registrations for an event",
        responses={
            200: EventRegistrationSerializer(many=True)
        }
    )
    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        event = self.get_object()
        registrations = event.registrations.filter(status='confirmed')
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Register for an event",
        responses={
            201: EventRegistrationSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Cancel event registration",
        responses={
            200: openapi.Response(
                description="Registration cancelled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        registration = get_object_or_404(
            EventRegistration, event=event, user=self.request.user
        )
        registration.status = 'cancelled'
        registration.save()
        return Response({'message': 'Registration cancelled successfully'})

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Toggle event featured status",
        responses={
            200: openapi.Response(
                description="Featured status updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'featured': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        event = self.get_object()
        event.featured = not event.featured
        event.save()
        return Response({'featured': event.featured})

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Toggle event status",
        responses={
            200: openapi.Response(
                description="Status updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        event = self.get_object()
        if event.status == 'draft':
            event.status = 'published'
        elif event.status == 'published':
            event.status = 'cancelled'
        event.save()
        return Response({'status': event.status})

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List event categories",
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = Event.objects.values_list('category', flat=True).distinct()
        return Response(categories)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Get event calendar",
        manual_parameters=[
            openapi.Parameter(
                'month',
                openapi.IN_QUERY,
                description="Month number (1-12)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Year",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="Calendar data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additionalProperties=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'category': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                )
            )
        }
    )
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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Save an event",
        responses={
            201: SavedEventSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
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

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Unsave an event",
        responses={
            200: openapi.Response(
                description="Event unsaved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        event = self.get_object()
        saved_event = get_object_or_404(SavedEvent, user=self.request.user, event=event)
        saved_event.delete()
        return Response({'message': 'Event unsaved successfully'})

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List saved events",
        responses={
            200: SavedEventSerializer(many=True)
        }
    )
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
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Mark review as helpful",
        responses={
            200: openapi.Response(
                description="Review marked as helpful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'helpful_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({'helpful_count': review.helpful_count})

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Report a review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Review reported successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        review = self.get_object()
        review.reported = True
        review.report_reason = request.data.get('reason', '')
        review.save()
        return Response({'message': 'Review reported successfully'})

class SavedEventViewSet(viewsets.ModelViewSet):
    queryset = SavedEvent.objects.all()
    serializer_class = SavedEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Create a saved event",
        request_body=SavedEventSerializer,
        responses={
            201: SavedEventSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List saved events",
        responses={
            200: SavedEventSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Create event registration",
        request_body=EventRegistrationSerializer,
        responses={
            201: EventRegistrationSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List event registrations",
        responses={
            200: EventRegistrationSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class EventSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = EventSubscription.objects.all()
    serializer_class = EventSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="Create event subscription",
        request_body=EventSubscriptionSerializer,
        responses={
            201: EventSubscriptionSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Events'],
        operation_description="List event subscriptions",
        responses={
            200: EventSubscriptionSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)