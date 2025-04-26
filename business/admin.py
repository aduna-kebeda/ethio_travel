from django.contrib import admin
from .models import Business, BusinessReview, SavedBusiness

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_type', 'region', 'city', 'status', 'is_verified', 'is_featured')
    list_filter = ('status', 'is_verified', 'is_featured', 'business_type', 'region', 'city')
    search_fields = ('name', 'description', 'contact_email', 'contact_phone')
    readonly_fields = ('slug', 'average_rating', 'total_reviews')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'business_type', 'description', 'contact_email', 'contact_phone', 'website')
        }),
        ('Location', {
            'fields': ('region', 'city', 'address', 'latitude', 'longitude')
        }),
        ('Multimedia', {
            'fields': ('main_image', 'gallery_images')
        }),
        ('Social Media', {
            'fields': ('social_media_links',)
        }),
        ('Operational Details', {
            'fields': ('opening_hours', 'facilities', 'services', 'team')
        }),
        ('Status', {
            'fields': ('status', 'is_verified', 'is_featured', 'verification_date')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Additional Data', {
            'fields': ('additional_data',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'owner')
        }),
    )

@admin.register(BusinessReview)
class BusinessReviewAdmin(admin.ModelAdmin):
    list_display = ('business', 'user', 'rating', 'is_reported', 'created_at')
    list_filter = ('rating', 'is_reported', 'created_at')
    search_fields = ('comment', 'business__name', 'user__username')
    readonly_fields = ('helpful_votes',)

@admin.register(SavedBusiness)
class SavedBusinessAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'business__name') 