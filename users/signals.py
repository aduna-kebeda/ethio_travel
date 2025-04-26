from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, BusinessOwnerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_business_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'business_owner' and not hasattr(instance, 'business_profile'):
        BusinessOwnerProfile.objects.create(user=instance)