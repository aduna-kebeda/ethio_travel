from django.contrib import admin
from .models import Booking, Payment, BookingReview

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'business', 'package', 'status', 'number_of_people', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'event__title', 'business__name', 'package__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'event', 'business', 'package', 'status')
        }),
        ('Booking Details', {
            'fields': ('number_of_people', 'special_requests')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking__user__email', 'transaction_id')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'amount', 'payment_method', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'payment_details')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(BookingReview)
class BookingReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'title', 'helpful', 'reported')
    list_filter = ('rating', 'reported')
    search_fields = ('title', 'content')
    readonly_fields = ('helpful', 'reported')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('booking', 'rating', 'title', 'content')
        }),
        ('Status', {
            'fields': ('helpful', 'reported')
        }),
    )