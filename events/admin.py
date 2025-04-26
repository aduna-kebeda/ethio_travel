from django.contrib import admin
from .models import Event, EventReview, EventRegistration, SavedEvent, EventSubscription

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organizer', 'start_date', 'end_date', 'status', 'featured', 'rating')
    list_filter = ('category', 'status', 'featured')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('slug', 'current_attendees', 'rating', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'organizer')
        }),
        ('Date and Time', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location', {
            'fields': ('location', 'address', 'latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('price', 'capacity', 'current_attendees', 'rating', 'images')
        }),
        ('Status', {
            'fields': ('featured', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'title', 'helpful', 'reported')
    list_filter = ('rating', 'reported')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Details', {
            'fields': ('event', 'user', 'rating', 'title', 'content')
        }),
        ('Feedback', {
            'fields': ('helpful', 'reported')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('event__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Registration Details', {
            'fields': ('event', 'user', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Saved Event Details', {
            'fields': ('user', 'event')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Subscription Details', {
            'fields': ('email', 'categories')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )