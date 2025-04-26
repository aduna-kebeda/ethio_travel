from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    tags = models.JSONField(default=list)
    imageUrl = models.URLField(max_length=500, blank=True)
    
    # Author Information
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    authorName = models.CharField(max_length=200, blank=True)
    authorImage = models.URLField(max_length=500, blank=True, null=True)
    
    # Status and Statistics
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    views = models.PositiveIntegerField(default=0)
    readTime = models.PositiveIntegerField()
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.authorName and self.author:
            self.authorName = self.author.get_full_name() or self.author.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Comment'
        verbose_name_plural = 'Blog Comments'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class SavedPost(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-saved_at']
        verbose_name = 'Saved Post'
        verbose_name_plural = 'Saved Posts'

    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"