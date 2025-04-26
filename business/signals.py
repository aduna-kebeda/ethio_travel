from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Business, BusinessReview

@receiver([post_save, post_delete], sender=BusinessReview)
def update_business_rating(sender, instance, **kwargs):
    """
    Signal to update business rating when a review is created, updated, or deleted
    """
    business = instance.business
    reviews = BusinessReview.objects.filter(business=business)
    
    if reviews.exists():
        total_rating = sum(review.rating for review in reviews)
        total_reviews = reviews.count()
        business.average_rating = total_rating / total_reviews
        business.total_reviews = total_reviews
    else:
        business.average_rating = 0
        business.total_reviews = 0
    
    business.save() 