from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DestinationViewSet, DestinationReviewViewSet, SavedDestinationViewSet

app_name = 'destinations'

router = DefaultRouter()
router.register(r'destinations', DestinationViewSet, basename='destination')
router.register(r'reviews', DestinationReviewViewSet, basename='review')
router.register(r'saved-destinations', SavedDestinationViewSet, basename='saved-destination')

urlpatterns = [
    path('', include(router.urls)),
]