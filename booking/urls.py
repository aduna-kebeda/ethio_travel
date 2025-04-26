from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, PaymentViewSet, BookingReviewViewSet

app_name = 'booking'

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', BookingReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]