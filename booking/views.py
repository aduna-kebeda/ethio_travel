from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Booking, Payment, BookingReview
from .serializers import (
    BookingListSerializer, BookingCreateSerializer,
    PaymentSerializer, BookingReviewSerializer
)
from .permissions import IsBookingOwner, IsPaymentOwner, IsReviewOwner
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBookingOwner]
    serializer_class = BookingListSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookingCreateSerializer
        return BookingListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Create a new booking",
        request_body=BookingCreateSerializer,
        responses={
            201: BookingCreateSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="List all bookings",
        responses={
            200: BookingListSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Retrieve a booking",
        responses={
            200: BookingListSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Update a booking",
        request_body=BookingCreateSerializer,
        responses={
            200: BookingCreateSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Delete a booking",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Cancel a booking",
        responses={
            200: openapi.Response(
                description="Booking cancelled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'cancelled':
            return Response(
                {'detail': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'cancelled'
        booking.save()
        return Response({'detail': 'Booking cancelled successfully'})

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="List upcoming bookings",
        responses={
            200: BookingListSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        queryset = self.get_queryset().filter(
            status='confirmed',
            event__start_date__gt=timezone.now()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsPaymentOwner]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user)

    def perform_create(self, serializer):
        booking = get_object_or_404(
            Booking,
            id=self.request.data.get('booking'),
            user=self.request.user
        )
        serializer.save(booking=booking)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Create a payment",
        request_body=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="List all payments",
        responses={
            200: PaymentSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Get payment history",
        responses={
            200: PaymentSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BookingReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsReviewOwner]
    serializer_class = BookingReviewSerializer

    def get_queryset(self):
        return BookingReview.objects.filter(booking__user=self.request.user)

    def perform_create(self, serializer):
        booking = get_object_or_404(
            Booking,
            id=self.request.data.get('booking'),
            user=self.request.user
        )
        serializer.save(booking=booking)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Create a booking review",
        request_body=BookingReviewSerializer,
        responses={
            201: BookingReviewSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="List all booking reviews",
        responses={
            200: BookingReviewSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Mark review as helpful",
        responses={
            200: openapi.Response(
                description="Review marked as helpful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'helpful': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful += 1
        review.save()
        return Response({'helpful': review.helpful})

    @swagger_auto_schema(
        tags=['Booking'],
        operation_description="Report a review",
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
        review.save()
        return Response({'message': 'Review reported successfully'})