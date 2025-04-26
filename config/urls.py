from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/business/', include('business.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/events/', include('events.urls')),
    path('api/destinations/', include('destinations.urls')),
    path('api/booking/', include('booking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 