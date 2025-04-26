from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PackageViewSet, PackageReviewViewSet, DepartureViewSet

app_name = 'packages'

router = DefaultRouter()
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'reviews', PackageReviewViewSet, basename='package-review')
router.register(r'departures', DepartureViewSet, basename='departure')

urlpatterns = [
    path('', include(router.urls)),
]