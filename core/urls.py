from django.urls import path
from .views import APIRootView

app_name = 'core'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
] 