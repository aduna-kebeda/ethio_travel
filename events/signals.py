from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Event, EventReview, EventRegistration

@receiver(post_save, sender=EventReview)
def update_event_rating(sender, instance, **kwargs):
    event = instance.event
    reviews = event.reviews.all()
    event.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
    event.save()

@receiver(post_delete, sender=EventReview)
def update_event_rating_on_delete(sender, instance, **kwargs):
    event = instance.event
    reviews = event.reviews.all()
    event.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
    event.save()

@receiver(post_save, sender=EventRegistration)
def update_event_attendees(sender, instance, **kwargs):
    event = instance.event
    event.current_attendees = event.registrations.filter(status='confirmed').count()
    event.save()

@receiver(post_delete, sender=EventRegistration)
def update_event_attendees_on_delete(sender, instance, **kwargs):
    event = instance.event
    event.current_attendees = event.registrations.filter(status='confirmed').count()
    event.save()