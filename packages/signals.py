from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Package, PackageReview

@receiver(post_save, sender=PackageReview)
@receiver(post_delete, sender=PackageReview)
def update_package_rating(sender, instance, **kwargs):
    package = instance.package
    reviews = package.reviews.all()
    package.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
    package.save()