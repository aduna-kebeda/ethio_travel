from django.contrib import admin
from .models import Package, PackageReview, SavedPackage, Departure

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'region', 'price', 'duration',
        'difficulty', 'featured', 'rating', 'status'
    ]
    list_filter = ['category', 'region', 'featured', 'difficulty', 'status']
    search_fields = ['title', 'description', 'location', 'region']
    readonly_fields = ['slug', 'rating']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'slug', 'description', 'short_description',
                      'location', 'region', 'price', 'discounted_price')
        }),
        ('Package Details', {
            'fields': ('duration', 'duration_in_days', 'image', 'gallery_images',
                      'category', 'included', 'not_included', 'itinerary')
        }),
        ('Schedule', {
            'fields': ('departure', 'departure_time', 'return_time')
        }),
        ('Requirements', {
            'fields': ('max_group_size', 'min_age', 'difficulty',
                      'tour_guide', 'languages')
        }),
        ('Additional Information', {
            'fields': ('coordinates', 'status', 'featured', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PackageReview)
class PackageReviewAdmin(admin.ModelAdmin):
    list_display = ['package', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['package__title', 'user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SavedPackage)
class SavedPackageAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'package__title']
    readonly_fields = ['created_at']

@admin.register(Departure)
class DepartureAdmin(admin.ModelAdmin):
    list_display = ['package', 'start_date', 'end_date', 'price', 'available_slots', 'is_guaranteed']
    list_filter = ['start_date', 'is_guaranteed']
    search_fields = ['package__title']
    readonly_fields = ['created_at', 'updated_at']