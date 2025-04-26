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