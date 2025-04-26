from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

User = get_user_model()

class Business(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    business_type = models.CharField(max_length=100)
    description = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)

    # Location Data
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Multimedia
    main_image = models.URLField(max_length=500)
    gallery_images = models.JSONField(default=list, blank=True)

    # Social Media
    social_media_links = models.JSONField(default=dict, blank=True)

    # Operational Details
    opening_hours = models.JSONField(default=dict, blank=True)
    facilities = models.JSONField(default=list, blank=True)
    services = models.JSONField(default=list, blank=True)
    team = models.JSONField(default=list, blank=True)

    # Status Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)

    # Rating and Review Statistics
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    # Additional Data
    additional_data = models.JSONField(default=dict, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_businesses')

    class Meta:
        verbose_name_plural = "Businesses"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['business_type']),
            models.Index(fields=['region']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class BusinessReview(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    helpful_votes = models.PositiveIntegerField(default=0)
    is_reported = models.BooleanField(default=False)
    report_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'user')
        indexes = [
            models.Index(fields=['business', 'user']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_reported']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_business_rating()

    def update_business_rating(self):
        business = self.business
        reviews = BusinessReview.objects.filter(business=business)
        total_rating = sum(review.rating for review in reviews)
        total_reviews = reviews.count()
        
        if total_reviews > 0:
            business.average_rating = total_rating / total_reviews
            business.total_reviews = total_reviews
            business.save()

    def __str__(self):
        return f"Review by {self.user.username} for {self.business.name}"

class SavedBusiness(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_businesses')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'business')
        indexes = [
            models.Index(fields=['user', 'business']),
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.business.name}" 