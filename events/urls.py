from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet, EventReviewViewSet, SavedEventViewSet,
    EventSubscriptionViewSet, EventRegistrationViewSet
)

app_name = 'events'

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'reviews', EventReviewViewSet, basename='review')
router.register(r'saved-events', SavedEventViewSet, basename='saved-event')
router.register(r'subscriptions', EventSubscriptionViewSet, basename='subscription')
router.register(r'registrations', EventRegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]