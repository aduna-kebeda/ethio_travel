from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from djongo import models as djongo_models
import json

User = get_user_model()

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField()
    content = models.TextField()
    tags = models.JSONField(default=list)
    imageUrl = models.URLField(max_length=500)
    
    # Author Information
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    authorName = models.CharField(max_length=200)
    authorImage = models.URLField(max_length=500, null=True, blank=True)
    
    # Status and Statistics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    readTime = models.CharField(max_length=50)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_blogpost'
        ordering = ['-createdAt']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_comment'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    savedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_savedpost'
        unique_together = ('user', 'post')
        ordering = ['-savedAt'] 