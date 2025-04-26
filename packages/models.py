from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from djongo.models import JSONField

User = get_user_model()

class Package(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Challenging', 'Challenging'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='packages', null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    location = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=50)
    duration_in_days = models.IntegerField()
    image = models.CharField(max_length=200, blank=True)  # GridFS ID or URL
    gallery_images = JSONField(default=list)  # Replace ArrayField with JSONField
    category = JSONField(default=list)  # Replace ArrayField with JSONField
    included = JSONField(default=list)  # Replace ArrayField with JSONField
    not_included = JSONField(default=list)  # Replace ArrayField with JSONField
    itinerary = JSONField(default=list)  # Replace ArrayField with JSONField
    departure = models.CharField(max_length=100)
    departure_time = models.TimeField()
    return_time = models.TimeField()
    max_group_size = models.IntegerField()
    min_age = models.IntegerField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    tour_guide = models.CharField(max_length=100)
    languages = JSONField(default=list)  # Replace ArrayField with JSONField
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    coordinates = JSONField(default=[0.0, 0.0])  # Replace ArrayField with JSONField
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['region']),
            models.Index(fields=['featured']),
            models.Index(fields=['status']),
        ]

class PackageReview(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='reviews', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='package_reviews', null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        package_name = self.package.title if self.package else 'No package'
        user_email = self.user.email if self.user else 'No user'
        return f"Review by {user_email} for {package_name}"

    class Meta:
        unique_together = ['package', 'user']
        indexes = [
            models.Index(fields=['package']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]

class SavedPackage(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_packages', null=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='saved_by', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        package_name = self.package.title if self.package else 'No package'
        user_email = self.user.email if self.user else 'No user'
        return f"{user_email} saved {package_name}"

    class Meta:
        unique_together = ['user', 'package']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['package']),
        ]

class Departure(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='departures', null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    available_slots = models.IntegerField(null=True)
    is_guaranteed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        package_name = self.package.title if self.package else 'No package'
        date = self.start_date if self.start_date else 'No date'
        return f"{package_name} - {date}"

    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['is_guaranteed']),
        ]