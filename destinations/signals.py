from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Destination, DestinationReview

@receiver(post_save, sender=DestinationReview)
def update_destination_rating(sender, instance, **kwargs):
    destination = instance.destination
    reviews = destination.reviews.all()
    destination.review_count = reviews.count()
    destination.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
    destination.save()

@receiver(post_delete, sender=DestinationReview)
def update_destination_rating_on_delete(sender, instance, **kwargs):
    destination = instance.destination
    reviews = destination.reviews.all()
    destination.review_count = reviews.count()
    destination.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
    destination.save()