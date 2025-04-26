from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from djongo.models import JSONField

User = get_user_model()

class Destination(models.Model):
    CATEGORY_CHOICES = (
        ('historical', 'Historical'),
        ('natural', 'Natural'),
        ('cultural', 'Cultural'),
        ('religious', 'Religious'),
        ('adventure', 'Adventure'),
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
    )
    
    REGION_CHOICES = (
        ('addis_ababa', 'Addis Ababa'),
        ('afar', 'Afar'),
        ('amhara', 'Amhara'),
        ('benishangul_gumuz', 'Benishangul-Gumuz'),
        ('diredawa', 'Dire Dawa'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('oromia', 'Oromia'),
        ('sidama', 'Sidama'),
        ('somali', 'Somali'),
        ('south_west', 'South West'),
        ('southern', 'Southern'),
        ('tigray', 'Tigray'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='destinations', null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    city = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.IntegerField(default=0)
    images = JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['region']),
            models.Index(fields=['featured']),
            models.Index(fields=['status']),
        ]

class DestinationReview(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='destination_reviews', null=True)
    rating = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    helpful = models.IntegerField(default=0)
    reported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.destination.title}"
    
    class Meta:
        indexes = [
            models.Index(fields=['destination']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]

class SavedDestination(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_destinations', null=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='saved_by', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} saved {self.destination.title}"
    
    class Meta:
        unique_together = ('user', 'destination')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['destination']),
        ]