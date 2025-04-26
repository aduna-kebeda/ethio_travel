from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from djongo.models import JSONField
import uuid
from bson import ObjectId
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

def generate_object_id():
    return str(ObjectId())

class User(AbstractUser):
    PROVIDER_CHOICES = [
        ('credentials', 'Credentials'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]
    
    ROLE_CHOICES = (
        ('user', 'User'),
        ('business_owner', 'Business Owner'),
        ('admin', 'Admin'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )
    
    id = models.CharField(primary_key=True, max_length=24, default=generate_object_id)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-z0-9_-]{3,20}$',
                message='Username must be 3-20 characters long and can only contain lowercase letters, numbers, underscores, and hyphens.'
            )
        ]
    )
    email = models.EmailField(unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='credentials')
    provider_id = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_expires = models.DateTimeField(blank=True, null=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_expires = models.DateTimeField(blank=True, null=True)
    login_attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(blank=True, null=True)
    interests = JSONField(default=list)
    image = models.CharField(max_length=200, blank=True, null=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='custom_user_set',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.lock_until = timezone.now() + timedelta(minutes=30)
        self.save()
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.lock_until = None
        self.save()
    
    def is_locked(self):
        return self.lock_until and self.lock_until > timezone.now()
    
    def generate_verification_code(self):
        self.verification_code = ''.join(random.choices('0123456789', k=6))
        self.verification_expires = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.verification_code
    
    def generate_reset_password_token(self):
        self.reset_password_token = str(uuid.uuid4())
        self.reset_password_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.reset_password_token
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    BUDGET_RANGE_CHOICES = [
        ('Budget', 'Budget'),
        ('Mid-range', 'Mid-range'),
        ('Luxury', 'Luxury'),
    ]
    
    id = models.CharField(primary_key=True, max_length=24, default=generate_object_id)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    preferred_currency = models.CharField(max_length=3, default='ETB')
    travel_interests = JSONField(default=list)
    accommodation_types = JSONField(default=list)
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGE_CHOICES, default='Mid-range')
    travel_style = JSONField(default=list)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_notifications = models.BooleanField(default=True)
    new_deals_notifications = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    trip_reminders = models.BooleanField(default=True)
    facebook = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

class BusinessOwnerProfile(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=generate_object_id)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100)
    business_description = models.TextField()
    business_phone = models.CharField(max_length=20)
    business_email = models.EmailField()
    business_website = models.URLField(blank=True, null=True)
    business_address = models.TextField()
    business_city = models.CharField(max_length=100)
    business_country = models.CharField(max_length=100)
    business_registration_number = models.CharField(max_length=100, blank=True, null=True)
    business_tax_id = models.CharField(max_length=100, blank=True, null=True)
    business_license = models.CharField(max_length=200, blank=True, null=True)
    business_logo = models.CharField(max_length=200, blank=True, null=True)
    business_photos = JSONField(default=list)
    business_social_media = JSONField(default=list)
    business_operating_hours = JSONField(default=list)
    business_payment_methods = JSONField(default=list)
    business_amenities = JSONField(default=list)
    business_cancellation_policy = models.TextField(blank=True)
    business_terms_conditions = models.TextField(blank=True)
    business_privacy_policy = models.TextField(blank=True)
    business_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    business_review_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, default='pending')
    verification_documents = JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} - {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]