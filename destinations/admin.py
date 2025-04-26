from django.contrib import admin
from .models import Destination, DestinationReview, SavedDestination

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'region', 'city', 'featured', 'rating', 'review_count')
    list_filter = ('category', 'region', 'featured', 'status')
    search_fields = ('title', 'description', 'address')
    readonly_fields = ('slug', 'rating', 'review_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'slug', 'description', 'category', 'region', 'city', 'address')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Media', {
            'fields': ('images',)
        }),
        ('Status', {
            'fields': ('featured', 'status', 'rating', 'review_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DestinationReview)
class DestinationReviewAdmin(admin.ModelAdmin):
    list_display = ('destination', 'user', 'rating', 'title', 'helpful', 'reported')
    list_filter = ('rating', 'reported')
    search_fields = ('title', 'content')
    readonly_fields = ('helpful', 'reported', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('destination', 'user', 'rating', 'title', 'content')
        }),
        ('Status', {
            'fields': ('helpful', 'reported')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SavedDestination)
class SavedDestinationAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'destination__title')
    readonly_fields = ('created_at',)