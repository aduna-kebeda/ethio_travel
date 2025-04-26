from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import BlogPost

@receiver(post_save, sender=BlogPost)
def update_published_at(sender, instance, created, **kwargs):
    """
    Update the date field when a post is published
    """
    if instance.status == 'published' and not instance.created_at:
        instance.created_at = timezone.now()
        instance.save(update_fields=['created_at']) 